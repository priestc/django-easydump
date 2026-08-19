import os

import boto3
from django.apps import apps
from django.conf import settings
from django.core.mail import send_mail
from django.core.management.base import BaseCommand

from easydump import dumpers

class Manifest:
    """
    Wrapper class that makes working with manifests easier.
    """
    def __init__(self, md):
        self.bucket_name = md.get('s3-bucket')
        self.database_name = md.get('database')
        self.exclude_models = md.get('exclude-models', [])
        self.include_models = md.get('include-models', None)
        self.extra_tables = md.get('extra-tables', [])
        self.jobs = md.get('jobs', 2)
        self.reduced_redundancy = md.get('reduced-redundancy', True)

        self.bucket = self._get_bucket()
        self.database = self._get_database()
        self.tables = self._get_tables()

        dumper = self._get_dumper()
        self.dump_cmd = dumper.get_dump_cmd(self)
        self.restore_cmd = dumper.get_restore_cmd(self)
        self.drop_cmd = dumper.get_drop_cmd(self)

    def _get_bucket(self):
        s3 = boto3.resource(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY,
            aws_secret_access_key=settings.AWS_SECRET_KEY,
            region_name=getattr(settings, 'AWS_REGION', 'us-east-1'),
        )
        return s3.Bucket(self.bucket_name)

    def _get_database(self):
        return settings.DATABASES[self.database_name]

    def _get_dumper(self):
        """
        Based on which kind of database theis manifest is for, get the proper
        dumper object.
        """
        engine = self.database['ENGINE']
        if 'postgis' in engine:
            return dumpers.PostgresDumper

        if 'postgresql' in engine:
            return dumpers.PostgresDumper

        if 'oracle' in engine:
            return dumpers.OracleDumper

        if 'mysql' in engine:
            return dumpers.MySQLDumper

    def _get_tables(self):
        """
        Return all the database tables that we are going to dump.
        """

        all_models = apps.get_models()
        dump_tables = []

        for model in all_models:
            model_name = model.__name__
            table_name = model._meta.db_table

            if self.include_models:
                # if an included-models is given, only add models that are
                # listed there
                add_to_dump = model_name in self.include_models
            else:
                # if no include-models is given, add everything, unless
                # explicitly excluded
                add_to_dump = model_name not in self.exclude_models

            if add_to_dump:
                dump_tables.append(table_name)

        return set(dump_tables + self.extra_tables)

class EasyDumpCommand(BaseCommand):
    """
    Common methods for all dump commands
    """

    def get_manifest(self, name):
        try:
            manifest_dict = settings.EASYDUMP_MANIFESTS[name]
        except KeyError:
            raise KeyError("Can't find manifest, is it in EASYDUMP_MANIFESTS?")

        return Manifest(manifest_dict)

    def notify_failure(self, subject, message):
        """
        Emails EASYDUMP_FAILURE_EMAIL (if configured in settings) to report
        a backup failure. Never raises - a broken mail config shouldn't mask
        the original failure that triggered this call.
        """
        recipient = getattr(settings, 'EASYDUMP_FAILURE_EMAIL', None)
        if not recipient:
            return

        recipients = recipient if isinstance(recipient, (list, tuple)) else [recipient]
        from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'easydump@localhost')

        send_mail(subject, message, from_email, recipients, fail_silently=True)