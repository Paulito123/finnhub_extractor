'''
This script creates a config file that can be read by the
application at execution time. All configurations should
reside in one or more configuration files, rather than
directly in the source code!!

Absolute paths can be used, for example C:\Program Files\Python
or relative paths like ..\config\private.

sp500 tickers > https://datahub.io/core/s-and-p-500-companies/r/0.html
nasdaq tickers > ftp://ftp.nasdaqtrader.com/SymbolDirectory/nasdaqlisted.txt
'''

import configparser

# The path of the config file that will be created or updated.
main_config_file = 'config/finnhub_extractor.conf'                                                              # Relative
# Create a "Parser" object that will process the given configuration.
config = configparser.ConfigParser()


# Local configurations.
config['local'] = {'target_path_xlsx': '/home/virtosa/raw_data/finnhub/xlsx'}                                   # Absolute

# Keys needed to query Finnhub.io
config['keys'] = {'key1': '',                                                                                   # Insert
                  'secret1': ''}

# Information related to the tickers to be iterated.
config['ticker'] = {'source_path_ticker_file': 'sources/tickers.txt'}                                           # Relative

# Path where the nasdaq ticker file can be downloaded and where it should be stored locally.
config['nasdaq'] = {'source_path_ftp': 'ftp://ftp.nasdaqtrader.com/SymbolDirectory/nasdaqlisted.txt',
                    'target_path': '/home/virtosa/PycharmProjects/finnhub_extractor/sources/nasdaqlisted.txt'}  # Absolute

# Download limits for Finnhub.io
config['limit'] = {'day_limit': '0',
                   'hour_limit': '60',
                   'minute_limit': '0'}

# Existing intervals on Finnhub.io
config['interval'] = {'1min': '1',
                      '5min': '5',
                      '15min': '15',
                      '30min': '30',
                      '60min': '60',
                      'day': 'D',
                      'week': 'W',
                      'month': 'M'}

# Create the actual configuration file.
with open(main_config_file, 'w') as configfile:
   config.write(configfile)

