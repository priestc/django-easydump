import datetime
import os
import logging
log = logging.getLogger(__name__)

from django.conf import settings
from easydump.mixins import EasyDumpCommand

from easydump.utils import key_parser

class Command(EasyDumpCommand):
    """
    Retrieve a dump file from S3, then apply it to the database
    """
    def handle(self, *args, **options):
        
        # get manifest
        dump = options['dump']
        manifest = self.get_manifest(dump)
        
        # get the key for the correct dump (the latest one)
        key = self.get_latest(manifest.bucket, dump)
        
        if not os.path.exists('easydump'):
            log.info("Downloading from S3...")
            key.get_contents_to_filename('easydump')
        else:
            log.info('not downloading because it already has been downloaded')
        
        # put into postgres
        cmd = manifest.restore_cmd
        os.system(cmd)
        os.remove('easydump')

    def get_latest(self, bucket, prefix):
        """
        Given a S3 bucket, return the key in that bucket named with the latest
        timestamp, AND has the given prefix.
        """
        none = datetime.datetime(1,1,1) # always be expired
        
        def p(name, prefix):
            """
            A new parser function because the sorted() function can't compare 
            datetime objects with None, so instead of None, return a really really
            old datetime object.
            """
            return key_parser(name, prefix) or none
        
        keys = [{'dt': p(k.name, prefix), 'string': k.name} for k in bucket.list()]
        latest = sorted(keys, key=lambda x: x['dt'])[-1]
        key = latest['string']
        dt = latest['dt']
        
        assert dt is not none, "Can't find any dumps in bucket"
        
        log.info("Using latest dump from: {0:%B %d, %Y -- %X}".format(dt))
        return bucket.get_key(key)