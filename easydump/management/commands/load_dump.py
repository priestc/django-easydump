import os
from optparse import make_option
import logging
log = logging.getLogger(__name__)

from dateutil.parser import parse
from django.conf import settings
from easydump.mixins import EasyDumpCommand

class Command(EasyDumpCommand):
    """
    Retrieve a dump file from S3, then apply it to the database
    """
    def handle(self, *args, **options):
        
        # get manifest
        dump = options['dump']
        manifest = self.get_manifest(dump)
        
        # get the key for the correct dump (the latest one)
        key = self.get_latest(bucket)
        
        save_path = manifest.get_save_template().format(key=key)
        
        if not os.path.exists(save_path):
            log.info("Downloading from S3...")      
            key.get_contents_to_filename(save_path)
            log.info("Done")
        else:
            log.info('not downloading because it already has been downloaded')
        
        # put into postgres
        cmd = restore_cmd.format(manifest=manifest)
        os.system(cmd)

    def get_latest(self, bucket):
        """
        Given a S3 bucket, return the key in that bucket named with the latest
        timestamp.
        """
        keys = [{'dt': parse(k.name), 'string': k.name} for k in bucket.list()]
        latest = sorted(keys, key=lambda x: x['dt'])[-1]
        key = latest['string']
        dt = latest['dt']
        log.info("Using latest dump from: {0:%B %m, %y -- %X}".format(dt))
        return bucket.get_key(key)