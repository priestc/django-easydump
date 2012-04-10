import os

from django.conf import settings
from django.core.management.base import NoArgsCommand
from django.db import models

from boto.s3.connection import S3Connection

class Manifest(object):
    
    def __init__(self, md):
        self.save_location = md.get('save-location', '.')
        self.bucket_name = md.get('s3-bucket')
        self.database_name = md.get('database')
        self.exclude_models = md.get('exclude-models', [])
        self.include_models = md.get('include-models', None)
        
        self.bucket = self._get_bucket()
        self.database = self._get_database()
        self.tables = self._get_tables()
        
    def _get_bucket(self):
        conn = S3Connection(settings.AWS_ACCESS_KEY, settings.AWS_SECRET_KEY)
        return conn.get_bucket(manifest['s3-bucket'])       

    def _get_database(self):
        database = settings.DATABASES[self.database_name]
        
        # sanity checks
        engine = database['ENGINE']
        is_postgres = 'postgis' in engine or 'postgresql' in engine
        assert is_postgres, "Sorry, only postgres/postgis supported at this time"

        return database

    def _get_tables(self):
        """
        return all the database tables that we are going to dump.
        """

        all_models = model.get_models()
        dump_tables = []

        for model in all_models:
            model_name = model.__name__
            table_name = model._meta.db_table

            if included_models:
                # if an included-models is given, only add models that are
                # listed there
                add_to_dump = model_name in self.include_models
            else:
                # if no include-models is given, add everything, unless
                # explicitly excluded
                add_to_dump = model_name not in self.exclude_models

            if add_to_dump:
                dump_models.append(table_name)

        return dump_tables

class EasyDumpCommand(NoArgsCommand):
    """
    Common methods for all dump commands
    """
    
    option_list = NoArgsCommand.option_list + (
        make_option(
            '--dump',
            '-d',
            dest='dump',
            help="Dump to perform",
        ),
    )
    
    def get_manifest(self, name):
        try:
            manifest_dict = settings.EASYDUMP_MANIFESTS[dump]
        except KeyError:
            raise KeyError("Can't find manifest, is it in EASYDUMP_MANIFESTS?")
        
        return Manifest(manifest_dict)