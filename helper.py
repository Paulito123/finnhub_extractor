from datetime import datetime, timedelta
import custom_types as ct
import time


class Helpers:

    @staticmethod
    def print_timestamped_text(text=""):
        """Prints a timestamped string."""
        dto = datetime.now()
        print('[{}] '.format(dto) + text)

    @staticmethod
    def generate_event_output(error_type, print_it=False, description=None):
        '''Returns a standardized event dictionary and prints the event status if required.'''
        output = {'description': ct.EventDescription.get_event_description(error_type
        ) if description is None else description,
                  'error_type': ct.EventType.NO_ERROR}

        if print_it:
            Helpers.print_timestamped_text('Event occurred with description [{}].'.format(output['description']))

        return output


    @staticmethod
    def sleep_handler(nr_of_secs=1):
        """Sleeps for a number of seconds, while printing the remaining number of seconds, every 15th seconds."""

        print("Sleeping {} sec > ".format(nr_of_secs), end="", flush=True)
        for x in range(nr_of_secs, 0, -1):
            time.sleep(1)
            if x % 15 == 0:
                print(".{}".format(x), end="", flush=True)
        print('Wake up!')

    @staticmethod
    def remove_newlines_from_str_list(string_list):
        converted_list = []
        for element in string_list:
            converted_list.append(element.strip())
        return converted_list

    @staticmethod
    def datetime_string_to_epoch(dt_str):
        try:
            epoch = datetime.strptime(dt_str, "%Y-%m-%dT%H:%M:%S.%fZ").timestamp()
            return int(epoch)
        except ValueError:
            pass

        try:
            epoch = datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S").timestamp()
            return int(epoch)
        except ValueError:
            pass

        try:
            epoch = datetime.strptime(dt_str, "%Y-%m-%d %H:%M").timestamp()
            return int(epoch)
        except ValueError:
            pass

        try:
            epoch = datetime.strptime(dt_str, "%Y-%m-%d").timestamp()
            return int(epoch)
        except ValueError:
            pass

        return 0