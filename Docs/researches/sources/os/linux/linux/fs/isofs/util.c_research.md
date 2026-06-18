# File Research: sources/os/linux/linux/fs/isofs/util.c

Provides ISO9660 timestamp conversion.

`iso_date()` converts short or long ISO date formats into `struct timespec64`:
- Long form parses ASCII year/month/day/hour/min/sec/hundredths and timezone.
- Short form parses numeric year since 1900, month/day/time, and optional timezone; High Sierra has no timezone.
- Negative years map to zero seconds.
- Timezone is sign-extended and accepted only within ±52 fifteen-minute units, then subtracted to convert local recorded time to GMT.

Used by inode and Rock Ridge timestamp parsing.
