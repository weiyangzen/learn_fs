# File Research: sources/os/plan9/9front/sys/src/lib9p/util.c

## Read Status
Complete: 24 lines read.

## Purpose
Provides simple read response helpers for static buffers and strings.

## Important Functions
- `readbuf`: copies a byte range from a buffer into `r->ofcall.data` according to request offset/count and clamps at EOF.
- `readstr`: calls `readbuf` for a NUL-terminated string.

## Dependencies and Interactions
- Intended for simple 9P read handlers serving static text or memory buffers.
- Sets `r->ofcall.count` but does not call `respond`; caller remains responsible for responding.
