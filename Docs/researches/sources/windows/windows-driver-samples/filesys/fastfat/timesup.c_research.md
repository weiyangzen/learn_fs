# File Research: sources/windows/windows-driver-samples/filesys/fastfat/timesup.c

## Role

`timesup.c` implements FAT/NT timestamp conversion. It bridges Windows system time, local time, FAT date/time bitfields, and FAT creation-time 10-millisecond subsecond storage.

## Key Routines

- `FatNtTimeToFatTime`: converts an NT `LARGE_INTEGER` timestamp to a FAT timestamp, optionally rounding up to the next FAT two-second boundary. It converts system time to local time, validates FAT’s 1980-2107 year range, fills FAT date/time fields, optionally returns 10ms remainder data, then normalizes the input NT time back to the rounded/truncated representable value.
- `FatFatDateToNtTime`: converts a FAT date-only value to an NT system time at local midnight. Invalid FAT date fields produce zero time.
- `FatFatTimeToNtTime`: converts FAT date/time plus optional 10ms creation-time units into NT system time. It handles odd seconds from the 10ms field and clamps impossible second values above 59.
- `FatGetCurrentFatTime`: queries current system time, converts to local time, rounds up by almost two seconds, and returns the current FAT timestamp.

## Important Mechanics

FAT stores ordinary timestamps at two-second resolution, while creation time can include a 10ms field. The conversion logic preserves this distinction: non-rounded conversions retain a 10ms remainder when requested, while rounded conversions report zero remainder because the NT time has effectively been advanced to a FAT boundary.

All NT-to-FAT conversion is local-time based, matching FAT on-disk semantics. FAT-to-NT conversion turns local FAT fields back into system time.

## Dependencies And Coupling

The file uses `RtlTimeToTimeFields`, `RtlTimeFieldsToTime`, `ExSystemTimeToLocalTime`, `ExLocalTimeToSystemTime`, and `KeQuerySystemTime`. It is called by FCB/DCB creation and metadata update paths that need to populate or persist FAT directory timestamps.
