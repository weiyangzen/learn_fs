# File Research: sources/os/plan9/9front/sys/src/lib9p/dirread.c

## Read Status
Complete: 39 lines read.

## Purpose
Provides a helper for implementing directory reads from a callback-style directory generator.

## Main Responsibilities
- Track directory entry index across reads using `r->fid->dirindex`.
- Call a `Dirgen` callback to fill `Dir` records.
- Pack directory entries with `convD2M` into the response buffer.
- Free dynamically allocated `Dir` string fields after packing.

## Important Function
- `dirread9p`: fills `r->ofcall.data` with serialized directory entries until the request buffer is full or the generator is exhausted.

## Dependencies and Interactions
- Used by 9P server implementations that do not use lib9p’s built-in `File` tree readdir path.
- Relies on 9P `Dir` serialization rules and `BIT16SZ` minimum packed-size check.
