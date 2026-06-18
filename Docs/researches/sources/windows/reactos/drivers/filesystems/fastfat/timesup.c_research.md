# File Research: sources/windows/reactos/drivers/filesystems/fastfat/timesup.c

This file implements conversion between NT system time and FAT date/time formats.

Key responsibilities:
- Convert NT `LARGE_INTEGER` timestamps to FAT date/time stamps.
- Convert FAT dates and FAT date/time stamps back to NT time.
- Preserve FAT’s local-time semantics by converting between system and local time.
- Handle FAT’s 2-second timestamp granularity and optional 10-millisecond creation-time field.
- Return the current time in FAT timestamp format.

Important functions:
- `FatNtTimeToFatTime`: converts NT GMT time to local FAT date/time, optionally rounding up to the next FAT 2-second boundary. It can also return the 10-millisecond remainder for creation times.
- `FatFatDateToNtTime`: converts a FAT date-only value to NT GMT midnight local date.
- `FatFatTimeToNtTime`: converts a full FAT timestamp plus 10-millisecond creation subfield to NT GMT time.
- `FatGetCurrentFatTime`: queries current system time, converts to local time, rounds up to FAT 2-second granularity, and returns a FAT timestamp.

Notable behavior and risks:
- FAT timestamp range is limited to 1980 through 2107; `FatNtTimeToFatTime` returns false outside that range.
- `FatNtTimeToFatTime` mutates the input `NtTime` to the rounded/truncated representable value.
- Invalid FAT date/time fields convert to zero NT time.
- Seconds greater than 59 after applying the 10-millisecond field are truncated to zero.
