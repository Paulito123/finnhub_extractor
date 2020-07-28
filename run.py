import configparser
import nasdaq as nq
import os
import finnhub_connector as fc
import custom_types as ct
from helper import Helpers as hp


def load_ticker_files():
    '''
    Main process to be configured to start loading batches of tickers from Finnhub.io.
    :return: void
    '''

    # Parameters:
    # conf_file: path to the configuration file.
    # filetype: could be one of:
    #   custom  > Text file with only one column with the symbols, and NO HEADER!
    #   nasdaq  > Text file as it is downloaded from nasdaq ftp server, first column has the symbols.
    #   sp500   > Text file with tab delimiters, first column has the symbols. NO HEADER!
    params = {'conf_file': 'config/finnhub_extractor.conf',
              'filetype': ct.TickerFileType.SP500,
              'ticker_file_path': 'sources/sp500_tickers.txt',
              'intervals': ["60", "D"],
              'from': '2020-07-01 16:00:00',
              'to': '2020-07-03 00:00:00'}

    # Load configurations
    project_dir = os.path.dirname(os.path.abspath(__file__))
    conf_file = project_dir + '/' + params['conf_file']
    config = configparser.ConfigParser()
    config.read(conf_file)

    nq_obj = nq.Nasdaq(config)
    result = nq_obj.fetch_nq_ticker_file()
    if result['status_code'] == -1:
        hp.print_timestamped_text('Error copying nasdaq ticker file from ftp server.')
        quit()

    fh = fc.Finnhub(config)
    fh.fetch_timeseries(params['filetype'],
                        params['ticker_file_path'],
                        params['intervals'],
                        params['from'],
                        params['to'])


# From here on starts the code that is actually being executed:
if __name__ == "__main__":
    load_ticker_files()
