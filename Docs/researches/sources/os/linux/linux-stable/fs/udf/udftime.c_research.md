# File Research: sources/os/linux/linux-stable/fs/udf/udftime.c

## Summary
Converts between UDF on-disk timestamp structures and Linux `timespec64`.

## Main Responsibilities
- Converts disk timestamps to UTC seconds/nanoseconds, applying type-1 timezone offsets.
- Treats unspecified timezone offset `-2047` as zero.
- Sanitizes invalid centisecond/hundreds-of-microseconds/microseconds fields.
- Converts Linux time to UDF timestamp using `sys_tz.tz_minuteswest`.

## Important Behavior
Leap seconds are explicitly not handled. Sub-second fields are accepted only when each component is below 100; otherwise nanoseconds are set to zero.

## Risks
Timezone conversion depends on system timezone state when writing timestamps. Broken media with bogus sub-second fields is tolerated by dropping nanoseconds.
