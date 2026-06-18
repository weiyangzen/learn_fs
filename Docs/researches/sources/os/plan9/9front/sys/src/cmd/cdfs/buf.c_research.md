# File Research: sources/os/plan9/9front/sys/src/cmd/cdfs/buf.c

Buffered block I/O wrapper for `cdfs` track reading and writing.

Key behavior:
- `bopen` allocates a `Buf`, block buffer, and optional internal cache sized by block size and number of blocks.
- `bread` services arbitrary byte reads from block-oriented media by reading whole blocks through the device callback, caching aligned data, and copying requested byte ranges.
- `bwrite` buffers byte writes into full blocks and calls the write callback when the buffer fills.
- `bterm` flushes pending writes and frees buffer state.

Dependencies:
- Includes Plan 9 libc, disk headers, `dat.h`, and `fns.h`.
- Uses the callback stored in `Buf.fn`, normally MMC read/write routines.

Research notes:
- This layer bridges 9P byte-oriented reads/writes and MMC sector-oriented I/O.
- Short final writes depend on `bterm`/close to flush buffered data.
