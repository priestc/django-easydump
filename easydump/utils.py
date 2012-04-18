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

def progress_callback(bytes_done, bytes_togo):
    """
    Print out the progress of the current upload/download.
    """
    if bytes_togo == 0:
        return 
    percent = (bytes_done / float(bytes_togo)) * 100
    log.info("%2.2f%% done" % percent)


def human_size(size_bytes):
    """
    format a size in bytes into a 'human' file size, e.g. bytes, KB, MB, GB, TB, PB
    Note that bytes/KB will be reported in whole numbers but MB and above will have greater precision
    e.g. 1 byte, 43 bytes, 443 KB, 4.3 MB, 4.43 GB, etc
    """
    if size_bytes == 1:
        # because I really hate unnecessary plurals
        return "1 byte"

    suffixes_table = [('bytes',0),('KB',0),('MB',1),('GB',2),('TB',2), ('PB',2)]

    num = float(size_bytes)
    for suffix, precision in suffixes_table:
        if num < 1024.0:
            break
        num /= 1024.0

    if precision == 0:
        formatted_size = "%d" % num
    else:
        formatted_size = str(round(num, ndigits=precision))

    return "%s %s" % (formatted_size, suffix)