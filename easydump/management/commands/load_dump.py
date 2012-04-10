import datetime
import os
import logging
log = logging.getLogger(__name__)

from dateutil.parser import parse as iso_parse
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
        
        def parser(key):
            """
            given a key, parse out the prefix and parse into a datetime object
            (for comparison)
            """
            
            try:
                key_prefix, iso_date = key.split('|')
            except:
                # some weird key that was not put there by easydump
                log.info("found weird key: %s" % key)
                return none
            
            if prefix == key_prefix:
                return iso_parse(iso_date)
            else:
                log.info("wrong prefix: %s" % key)
                return none
        
        keys = [{'dt': parser(k.name), 'string': k.name} for k in bucket.list()]
        latest = sorted(keys, key=lambda x: x['dt'])[-1]
        key = latest['string']
        dt = latest['dt']
        
        assert dt is not none, "Can't find any dumps in bucket"
        
        log.info("Using latest dump from: {0:%B %d, %Y -- %X}".format(dt))
        return bucket.get_key(key)