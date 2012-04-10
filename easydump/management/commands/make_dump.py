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
            log.info("Dumping database to file...")
            os.system(manifest.dump_cmd)
        else:
            log.debug("Skipping postgres dump because it already exists")

        # make a key into the bucket where we will put the dump
        k = Key(manifest.bucket)
        k.key = "%s|%s" % (dump, datetime.datetime.now().isoformat())

        # upload file
        log.info("uploading %s to s3://%s/..." % (k.key, manifest.bucket_name))
        k.set_contents_from_filename('dump', reduced_redundancy=manifest.reduced_redundancy)

        # clean up
        os.remove('dump')
        
        log.info("Data Dump Successfully Uploaded.")