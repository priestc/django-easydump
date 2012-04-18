import datetime
import os
import time
import logging
log = logging.getLogger(__name__)

from boto.s3.key import Key
from easydump.mixins import EasyDumpCommand
from easydump.utils import human_size, progress_callback

class Command(EasyDumpCommand):

    def handle(self, *args, **options):
        
        dump = args[0]
        manifest = self.get_manifest(dump)
        
        # do the dump only if it already hasn't been done yet
        if not os.path.exists('easydump'):
            log.info("Dumping database to file...")
            log.debug("dump command: %s" % manifest.dump_cmd)
            os.system(manifest.dump_cmd)
        else:
            log.debug("Skipping postgres dump because it already exists")

        size = os.path.getsize('easydump')
        log.info('resulting dump is %s' % human_size(size))

        # make a key into the bucket where we will put the dump
        k = Key(manifest.bucket)
        k.key = "%s|%s" % (dump, datetime.datetime.now().isoformat())

        # upload file
        log.info("uploading %s to s3://%s/..." % (k.key, manifest.bucket_name))
        k.set_contents_from_filename(
            'easydump',
            reduced_redundancy=manifest.reduced_redundancy,
            cb=progress_callback)

        # clean up
        os.remove('easydump')
        
        log.info("Data Dump Successfully Uploaded.")