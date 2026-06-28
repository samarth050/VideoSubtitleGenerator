class TimeCode:

    @staticmethod
    def timestamp_to_ms(timestamp):

        hh, mm, rest = timestamp.split(":")

        ss, ms = rest.split(",")

        return (

            int(hh) * 3600000 +

            int(mm) * 60000 +

            int(ss) * 1000 +

            int(ms)

        )

    @staticmethod
    def ms_to_timestamp(milliseconds):

        hh = milliseconds // 3600000

        milliseconds %= 3600000

        mm = milliseconds // 60000

        milliseconds %= 60000

        ss = milliseconds // 1000

        ms = milliseconds % 1000

        return (

            f"{hh:02}:"

            f"{mm:02}:"

            f"{ss:02},"

            f"{ms:03}"

        )

    @staticmethod
    def format(milliseconds):

        return TimeCode.ms_to_timestamp(milliseconds)