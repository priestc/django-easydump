import datetime
import os
import logging
log = logging.getLogger(__name__)

from django.conf import settings
from easydump.mixins import EasyDumpCommand

from easydump.utils import key_parser, progress_callback

class Command(EasyDumpCommand):
    """
    Retrieve a dump file from S3, then apply it to the database
    """

    def add_arguments(self, parser):
        parser.add_argument('--manifest', '-m', type=str, default='default',
                            help="The manifest to load as specified in "
                                 "EASYDUMP_MANIFESTS [default='default']")
        parser.add_argument('--drop', '-d', action='store_true',
                            help="Drop & recreate the database before loading")

    def handle(self, *args, **options):
        
        # get manifest
        dump = options['manifest']
        manifest = self.get_manifest(dump)
        
        # get the key for the correct dump (the latest one)
        key = self.get_latest(manifest.bucket, dump)
        
        if not os.path.exists('easydump'):
            log.info("Downloading from S3...")
            key.get_contents_to_filename('easydump', cb=progress_callback)
        else:
            log.info('Skipping download because it already has been downloaded')

        # drop if requested
        if options['drop']:
            cmd = manifest.drop_cmd
            log.debug("drop command: %s" % cmd)
            import pdb; pdb.set_trace()
            os.system(cmd)

        # put into postgres
        cmd = manifest.restore_cmd
        log.debug("restore command: %s" % cmd)
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