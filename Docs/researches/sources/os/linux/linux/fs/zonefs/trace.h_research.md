# File Research: sources/os/linux/linux/fs/zonefs/trace.h

## Purpose

Defines zonefs tracepoints for zone management, direct append writes, and iomap mappings.

## Main Responsibilities

- Declares `zonefs_zone_mgmt` trace event.
- Declares `zonefs_file_dio_append` trace event.
- Declares `zonefs_iomap_begin` trace event.
- Sets trace include path and includes `trace/define_trace.h`.

## Important Invariants

- Trace events record device major/minor and inode/zone identifying data.
- Zone management traces derive file inode number from zone sector and zone-size shift.
- Iomap traces capture address, offset, and length.

## Dependencies

Linux tracepoint infrastructure, block operation string helpers, and zonefs structures.

## Research Notes

Tracing support for diagnosing zone management and block mapping behavior.
