import os
import shutil
import urllib.request as request
from helper import Helpers as hp
from contextlib import closing
import custom_types as ct


class Nasdaq:
    def __init__(self, config):
        self._config = config

    def fetch_nq_ticker_file(self):
        """check if nasdaq file exists, if not, fetch it"""

        # Local variables
        nasdaq_file = self._config['nasdaq']['target_path']

        try:
            if not os.path.isfile(nasdaq_file):
                with closing(request.urlopen(self._config['nasdaq']['source_path_ftp'])) as r:
                    with open(nasdaq_file, 'wb') as f:
                        shutil.copyfileobj(r, f)

            return hp.generate_event_output(
                ct.ErrorType.NO_ERROR,
                description='Nasdaq file copied from FTP server, or it was already present.'
            )

        except:
            return hp.generate_event_output(
                ct.EventType.ERROR_FILE_NOT_FETCHED,
                print_it=True,
                description='Nasdaq file could not be copied from FTP server and it is missing.')


