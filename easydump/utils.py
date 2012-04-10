from dateutil.parser import parse as iso_parse
import logging
log = logging.getLogger(__name__)

def key_parser(key, prefix):
    """
    Given a key, parse out the prefix and parse the iso date into a datetime
    object (for comparison).
    """
    try:
        key_prefix, iso_date = key.split('|')
    except:
        # some weird key that was not put there by easydump
        log.debug("found weird key: %s" % key)
        return None
    
    if prefix == key_prefix:
        return iso_parse(iso_date)
    else:
        # a dump from another manifest
        log.debug("wrong prefix: %s" % key)
        return None