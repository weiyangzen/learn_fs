# File Research: sources/os/linux/linux-stable/fs/isofs/util.c

Provides ISO timestamp conversion.

`iso_date()` supports:
- Short 7-byte ISO/High Sierra timestamps.
- Long-form Rock Ridge timestamps.
- Timezone conversion from 15-minute units to UTC.
- High Sierra mode with no timezone byte.
- Sanity bound of +/- 13 hours for timezone offsets.
- Nanosecond conversion from long-form hundredths of a second.

Invalid negative years return zero seconds.
