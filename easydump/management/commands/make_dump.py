import datetime
import os
import time
import logging
log = logging.getLogger(__name__)

from boto.s3.key import Key
from easydump.mixins import EasyDumpCommand

class Command(EasyDumpCommand):

    def handle(self, *args, **options):
        
        dump = options['dump']
        manifest = self.get_manifest(dump)
        
        # do the dump only if it already hasn't been done yet
        if not os.path.exists('dump'):
            log.info("Dumping postgres to file...")
            os.system(cmd)
        else:
            print("Skipping postgres dump because it already exists")

        bucket = self.get_bucket(manifest)
        k = Key(bucket)
        k.key = datetime.datetime.now().isoformat()

        # upload file
        log.info("uploading %s to S3..." % k.key)
        k.set_contents_from_filename('dump', reduced_redundancy=True)

        # clean up
        os.remove('this_dump')
        
        log.ingo("Data Dump Successfully Uploaded.")