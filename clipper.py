from clipboard import paste, copy
from time import sleep
from os import path
from fnmatch import fnmatch
import logging
import traceback
import requests
import signal

# setup logging
logger = logging.getLogger('clipper')
logger.setLevel(logging.DEBUG)
logger_file = path.join(path.dirname(path.normpath(__file__)), 'clipper.log')
logger_fh = logging.FileHandler(logger_file)
logger_fh.setLevel(logging.DEBUG)
logger_ch = logging.StreamHandler()
logger_ch.setLevel(logging.INFO)
logger_formatter = logging.Formatter('%(asctime)s:%(levelname)s:%(message)s')
logger_fh.setFormatter(logger_formatter)
logger.addHandler(logger_fh)
logger.addHandler(logger_ch)

# delay in seconds
delay = 1.5
is_exit = False


def main():
    global is_exit
    last_copied = paste()
    while not is_exit:
        try:
            copied = paste()
            if copied != last_copied:
                logger.info(f'Local Copied: {copied}')
                requests.get('http://3.137.207.173:8080/clipboard/' + copied)
                last_copied = copied
            remote = requests.get('http://3.137.207.173:8080/clipboard/').text;
            if remote != last_copied:
                copy(remote)
                logger.info(f'Remote Copied: {remote}')
                last_copied = remote
        except OSError as e:
            logger.error(str(e))
            logger.error(''.join(traceback.format_tb(e.__traceback__)))
        except Exception as e:
            logger.error(str(e))
            logger.error(''.join(traceback.format_tb(e.__traceback__)))
        sleep(delay)


def handler(signum, frame):
    global is_exit
    is_exit = True
    print("Receive a signal %d, is_exit = %d" % (signum, is_exit))


if __name__ == '__main__':
    try:
        signal.signal(signal.SIGINT, handler)
        signal.signal(signal.SIGTERM, handler)
        logger.info('Use "ctrl+c" to exit')
        main()
    except Exception as e:
        logger.error('Unhandled exception, program exited. Info follows.')
        logger.error(str(e))
        logger.error(''.join(traceback.format_tb(e.__traceback__)))
