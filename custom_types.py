from enum import Enum

# All different file types that are know in the system.
# custom: - No header
#         - Just one column with tickers
#         - no delimiter
# nasdaq: - Has header, first line should be skipped
#         - First column has the ticker
#         - Pipe (|) delimited
# sp500:  - No header
#         - First column has the ticker
#         - Tab (   ) delimited
# --> See finnhub_connector.fetch_timeseries for the configurations.


class TickerFileType(Enum):
    CUSTOM = 1
    SP500 = 2
    NASDAQ = 3


# All the custom error that occur in the application. Like this a better overview is created.
class EventType(Enum):
    UNKNOWN = 1
    NO_ERROR = 2
    ERROR_FILE_NOT_FETCHED = 3
    ERROR_FILETYPE_UNKNOWN = 4
    ERROR_FILE_MISSING = 5
    ERROR_FILE_EMPTY = 6
    ERROR_DATE_CONVERSION = 7
    ERROR_RESPONSE_FORMAT = 8


class EventDescription:
    def __init__(self):
        self.description_index = {
            EventType.UNKNOWN: "An unknown event happened.",
            EventType.NO_ERROR: "Finished successfully.",
            EventType.ERROR_FILE_NOT_FETCHED: "A file could not be fetched.",
            EventType.ERROR_FILETYPE_UNKNOWN: "Filetype is unknown.",
            EventType.ERROR_FILE_MISSING: "A file is missing.",
            EventType.ERROR_FILE_EMPTY: "A file is empty.",
            EventType.ERROR_DATE_CONVERSION: "Date conversion failed.",
            EventType.ERROR_RESPONSE_FORMAT: "Response not in the expected format."
        }

    def get_event_description(self, event_type):
        try:
            descr = self.description_index[event_type]
        except KeyError:
            descr = self.description_index[EventType.UNKNOWN]

        return descr
