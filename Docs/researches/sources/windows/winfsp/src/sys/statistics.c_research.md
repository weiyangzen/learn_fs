# File Research: sources/windows/winfsp/src/sys/statistics.c

## Purpose

`statistics.c` manages per-processor filesystem statistics buffers exposed through filesystem statistics queries.

## Main Contents

- `FspStatisticsCreate`
- `FspStatisticsDelete`
- `FspStatisticsCopy`

## Behavior

`FspStatisticsCreate`:

- Allocates an array of `FSP_STATISTICS`, one entry per processor.
- Zeroes the array.
- Initializes each entry's `FILESYSTEM_STATISTICS` base header.
- Reports filesystem type as `FILESYSTEM_STATISTICS_TYPE_FAT`.

`FspStatisticsDelete` frees the array.

`FspStatisticsCopy`:

- Rejects null output buffers.
- Requires at least `sizeof(FILESYSTEM_STATISTICS)` bytes.
- Computes the full statistics length as `sizeof(FSP_STATISTICS) * FspProcessorCount`.
- If the caller buffer is large enough, returns the full length and success.
- Otherwise returns `STATUS_BUFFER_OVERFLOW` and copies only the caller-provided length.
- Copies statistics into the caller buffer.

## Notable Details

- The implementation "pretends" to be FAT for statistics compatibility.
- Partial copies are allowed once the buffer can hold the common filesystem statistics header.
- Statistics storage is nonpaged.
