import datetime
import os
import subprocess
import time
import logging
log = logging.getLogger(__name__)

from easydump.mixins import EasyDumpCommand
from easydump.utils import human_size, make_progress_callback

class Command(EasyDumpCommand):

    def add_arguments(self, parser):
        parser.add_argument('--manifest', '-m', type=str, default='default',
                            help="The manifest to load as specified in "
                                 "EASYDUMP_MANIFESTS [default='default']")

    def handle(self, *args, **options):

        dump = options['manifest']
        manifest = self.get_manifest(dump)

        try:
            # do the dump only if it already hasn't been done yet
            if not os.path.exists('easydump'):
                log.info("Dumping database to file...")
                log.debug("dump command: %s" % manifest.dump_cmd)
                status = os.system(manifest.dump_cmd)
                if status != 0:
                    if os.path.exists('easydump'):
                        os.remove('easydump')
                    raise RuntimeError(
                        "Dump command exited with status %s, refusing to "
                        "upload: %s" % (status, manifest.dump_cmd))
            else:
                log.debug("Skipping postgres dump because it already exists")

            size = os.path.getsize('easydump')
            log.info('resulting dump is %s' % human_size(size))

            if 'postgres' in manifest.database['ENGINE']:
                log.info("Verifying dump integrity...")
                result = subprocess.call(
                    ['pg_restore', '--data-only', '-f', os.devnull, 'easydump'])
                if result != 0:
                    os.remove('easydump')
                    raise RuntimeError(
                        "Dump file failed integrity check (pg_restore exited "
                        "%s) - refusing to upload a corrupt/truncated backup" %
                        result)
                log.info("Dump integrity OK.")

            # the key where we will put the dump in the bucket
            key_name = "%s|%s" % (dump, datetime.datetime.now().isoformat())

            extra_args = {}
            if manifest.reduced_redundancy:
                extra_args['StorageClass'] = 'REDUCED_REDUNDANCY'

            # upload file
            log.info("uploading %s to s3://%s/..." % (key_name, manifest.bucket_name))
            manifest.bucket.upload_file(
                'easydump',
                key_name,
                ExtraArgs=extra_args,
                Callback=make_progress_callback(size))

            # clean up
            os.remove('easydump')

            log.info("Data Dump Successfully Uploaded.")

        except Exception as e:
            log.error("Backup failed for manifest '%s': %s" % (dump, e))
            self.notify_failure(
                subject="[easydump] backup FAILED for manifest '%s'" % dump,
                message="The easydump backup for manifest '%s' failed:\n\n%s"
                        % (dump, e))
            raise