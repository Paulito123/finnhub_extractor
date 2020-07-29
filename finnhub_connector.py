import os
import sys
import configparser
import datetime
import finnhub
import pandas as pd
import custom_types as ct
from collections import OrderedDict
from openpyxl import load_workbook
from helper import Helpers as hp

class Finnhub():
    def __init__(self, config):
        self._config = config
        self._fh_client = finnhub.Client(api_key='{}'.format(config['keys']['key1']))

    def create_filename(self, symbol, from_date, to_date, interval, extension=""):
        '''Create a filename from a set of given parameters'''
        from_dt = datetime.datetime.strptime(from_date, '%Y-%m-%d %H:%M:%S').strftime('%Y%m%d%H%M%S')
        to_dt = datetime.datetime.strptime(to_date, '%Y-%m-%d %H:%M:%S').strftime('%Y%m%d%H%M%S')
        return symbol + '_' + interval + '_' + from_dt + '_' + to_dt + '.' + extension

    def get_ticker_dataframe(self, filetype, ticker_file):
        '''Construct a pandas datafame from a ticker source files.'''
        # Check if ticker file exists
        if not os.path.isfile(ticker_file):
            return hp.generate_event_output(
                ct.EventType.ERROR_FILE_MISSING,
                description='Ticker file [{}] is missing.'.format(ticker_file))

        # Evaluate the file type
        if filetype == ct.TickerFileType.CUSTOM:

            # Open the file and start reading it line by line.
            with open(ticker_file) as tfile:

                # Iterate all the lines fetched from the file.
                lines = hp.remove_newlines_from_str_list(tfile.readlines())

                # If tickers are loaded, return the dataframe
                if len(lines) > 0:
                    return pd.DataFrame(lines, columns=["Symbol"])
                else:
                    return hp.generate_event_output(
                        ct.EventType.ERROR_FILE_EMPTY,
                        description='File [{}] is empty.'.format(ticker_file))

        elif filetype == ct.TickerFileType.SP500:
            # open for reading with "universal" type set to able to have tabbed delimiter
            df_ticker = pd.read_csv(ticker_file, delimiter='\t', header=None, names=["Symbol", "Name", "Sector"])
            df_ticker = df_ticker[["Symbol"]]
            return df_ticker
        elif filetype == ct.TickerFileType.NASDAQ:
            df_ticker = pd.read_csv(ticker_file, delimiter='|')
            df_ticker.drop(df_ticker.tail(1).index, inplace=True)
            df_ticker = df_ticker[["Symbol"]]
            return df_ticker
        else:
            return hp.generate_event_output(ct.EventType.ERROR_FILE_NOT_FETCHED)

    def fetch_timeseries(self, filetype, ticker_file, intervals, from_date, to_date):
        """
        Method that iterates ticker symbols from a source file and a list of intervals for each symbol. From and to
        date mark the bounds of the timeframe for which data is required.
        """
        # Set working variables
        target_path = self._config['local']['target_path_xlsx'] + '/'
        limit_counter = int(self._config['limit']['hour_limit']) - 1
        batch_start_time = datetime.datetime.now()

        # Create a dataframe from the list of tickers
        df_ticker = self.get_ticker_dataframe(filetype, ticker_file)

        # Iterate the tickers dataframe
        for symbol in df_ticker["Symbol"]:

            first_df = None

            # Iterate the intervals list
            for interval in intervals:

                if interval in ["2H", "4H"]:
                    if first_df is not None:
                        data = self.data_resample(first_df, interval)
                    else:
                        hp.print_timestamped_text("Conditions not met to resample data, skipping [{}]".format(interval))
                        continue
                else:
                    # Determine the interval part of the filename
                    interval_part = 'multi' if len(intervals) > 1 else interval

                    # Create target excel filename
                    target_file_path = target_path + self.create_filename(symbol, from_date, to_date, interval_part, 'xlsx')

                    # Introduce a sleep if the max calls limit has been reached (60/min)
                    if limit_counter == 0:
                        limit_counter = int(self._config['limit']['hour_limit']) - 1
                        nu = datetime.datetime.now()
                        delay = int((nu - batch_start_time).total_seconds()) + 1
                        batch_start_time = nu
                        hp.sleep_handler(delay)

                    # Get the data
                    data = self.data_download(symbol, interval, from_date, to_date)
                    limit_counter -= 1

                    # Get the data
                    if first_df is None:
                        first_df = data.copy()

                # Write data to Excel
                if data is not None:
                    self.write_timeseries_to_excel(symbol, interval, data, target_file_path)
                else:
                    hp.print_timestamped_text('No data to write [{}:{}]'.format(symbol, interval))

    @staticmethod
    def data_resample(dataframe, interval):
        '''Resample a given dataset to a higher timeframe'''
        try:
            return dataframe.resample(interval).agg(OrderedDict([('o', 'first'),
                                                                 ('h', 'max'),
                                                                 ('l', 'min'),
                                                                 ('c', 'last'),
                                                                 ('v', 'sum'), ])).dropna()
        except:
            return None

    def data_download(self, symbol, interval, from_date, to_date):
        '''Download data from finnhub.io'''
        try:
            # Convert dates.
            from_epoch = hp.datetime_string_to_epoch(from_date)
            to_epoch = hp.datetime_string_to_epoch(to_date)

            # check if dates are correctly converted.
            if from_epoch == 0 or to_epoch == 0:
                msg = "Dates could not be converted to epoch for symbol [{}:{}].".format(symbol, interval)
                hp.print_timestamped_text(msg)
                return None

            # Get data from Finnhub.io
            data = self._fh_client.stock_candles(symbol, interval, from_epoch, to_epoch)

            if len(data) > 0 and data['s'] == 'ok':
                # remove status column
                data.pop('s')

                # Convert the epoch formatted date to a readable date.
                data['t'] = pd.to_datetime(data['t'], unit='s')

                # Convert dict back to a dataframe to be able to export to excel.
                data = pd.DataFrame.from_dict(data)

                # Sort data according to time index
                data = data.set_index('t').sort_index()

                return data
            else:
                hp.print_timestamped_text('Could not download [{}:{}]'.format(symbol, interval))
                # Return None
                return None
        except:
            return None


    def write_timeseries_to_excel(self, symbol, interval, data, target_file_path):
        """
        Write data to a sheet in an existing or not yet existing excel file.
        """
        # define writer
        if os.path.isfile(target_file_path):
            book = load_workbook(target_file_path)
            writer = pd.ExcelWriter(target_file_path, engine='openpyxl')
            writer.book = book
        else:
            writer = pd.ExcelWriter(target_file_path, engine='xlsxwriter')

        # try to fetch data and write to excel
        try:
            # Write data to Excel
            data.to_excel(writer, sheet_name=interval, index=True, columns=['o', 'h', 'l', 'c', 'v'])

            # Return value
            msg = 'Data for [{}:{}] successfully exported to excel'.format(symbol, interval)
            return hp.generate_event_output(ct.EventType.NO_ERROR,
                                            description=msg,
                                            print_it=True)
        except FileNotFoundError:
            err_msg = 'Error: file {} was not found!'.format(target_file_path)
            return hp.generate_event_output(ct.EventType.ERROR_FILE_MISSING,
                                            description=err_msg,
                                            print_it=True)
        except:
            err_msg = "Unexpected error: {}".format(sys.exc_info()[0])
            return hp.generate_event_output(ct.EventType.ERROR_RESPONSE_FORMAT,
                                            description=err_msg,
                                            print_it=True)
        finally:
            writer.save()
            writer.close()
            pass


if __name__ == "__main__":
    '''
    fcl = finnhub.Client(api_key='bsfflsvrh5rf14r5njug')
    data = fcl.stock_candles('A', '1', 1593612000, 1593802800)
    print(data)
    '''
    params = {'conf_file': 'config/finnhub_extractor.conf',
              'filetype': 'sp500'}

    # Load configurations
    project_dir = os.path.dirname(os.path.abspath(__file__))
    conf_file = project_dir + '/' + params['conf_file']
    config = configparser.ConfigParser()
    config.read(conf_file)

    '''
    symbol = "AAPL"
    from_date = "2020-01-02 15:00:00"
    to_date = "2020-01-10 23:00:00"
    intervals = ["1"]
    interval_part = 'multi' if len(intervals) > 1 else intervals[0]
    target_path = config['local']['target_path_xlsx'] + '/'
    fh = Finnhub(config)
    target_file_path = target_path + fh.create_filename(symbol, from_date, to_date, interval_part, 'xlsx')
    '''
    fh = Finnhub(config)
    fh.fetch_timeseries(ct.TickerFileType.SP500, 'sources/sp500_tickers.txt', ["1", "D"], "2020-07-01 16:00:00", "2020-07-03 00:00:00")