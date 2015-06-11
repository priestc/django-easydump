from datetime import timedelta, datetime
import logging
log = logging.getLogger(__name__)

from dateutil import parser

from easydump.mixins import EasyDumpCommand

class Command(EasyDumpCommand):

    def add_arguments(self, parser):
        parser.add_argument('--manifest', '-m', type=str, default='default',
                            help="The manifest to load as specified in "
                                 "EASYDUMP_MANIFESTS [default='default']")
    
    def handle(self, *args, **options):
        
        dump = options['manifest']
        manifest = self.get_manifest(dump)
        
        two_weeks_ago = datetime.now() - timedelta(days=14)
        three_months_ago = datetime.now() - timedelta(days=90)
        
        keys = manifest.bucket.get_all_keys()
        
        for key in keys:
            dt = parser.parse(key.key)
            
            is_2_weeks_old = dt < two_weeks_ago
            is_3_months_old = dt < three_months_ago
            is_monday_9PM = dt.strftime("%w %H") == '1 18'
            
            if is_2_weeks_old:
                if is_monday_9PM:
                    log.debug("keep:", dt)
                else:
                    log.debug("delete:", dt)
                    key.delete()
            else:
                log.info("keep:", dt)
        
        log.info("Log Rotation Complete.")
