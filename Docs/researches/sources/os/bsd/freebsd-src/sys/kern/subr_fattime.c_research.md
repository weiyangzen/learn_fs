# File Research: sources/os/bsd/freebsd-src/sys/kern/subr_fattime.c

## Purpose
Converts between POSIX `timespec` values and MS-DOS/FAT date, time, and hundredths-of-second timestamp fields.

## Key Elements
- Forward conversion: `timespec2fattime()`.
- Reverse conversion: `fattime2timespec()`.
- Four-year leap-cycle constants and month tables: `mtab`, `daytab`.
- Local/UTC behavior controlled by the `utc` argument.
- Optional standalone test driver under `TEST_DRIVER`.

## Behavior
FAT date fields encode year since 1980, month, and day. FAT time fields encode hour, minute, and two-second units. The optional hundredths byte stores second parity and hundredths.

`timespec2fattime()` optionally adjusts by `utc_offset()`, emits hundredths, packs time fields, clamps pre-1980 dates to 1980-01-01, handles leap-year cycles, and corrects the non-leap year 2100. `fattime2timespec()` unpacks fields, reconstructs day count using `daytab`, applies the 2100 correction in reverse, adds the 1970-to-1980 offset, and optionally applies local timezone offset.

## Research Notes
The implementation avoids per-year loops by using four-year cycle tables, but FAT's range through 2107 requires special handling because 2100 breaks the simple every-four-years rule.
