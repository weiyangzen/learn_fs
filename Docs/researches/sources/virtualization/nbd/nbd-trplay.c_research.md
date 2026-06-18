# File Research: sources/virtualization/nbd/nbd-trplay.c

## Purpose
Implements `nbd-trplay`, a transaction-log replay tool that applies logged write-like operations to an existing disk image.

## Main Entry Points
- `main()` parses `-i`, `-l`, `-m`, `-b`, `-v`, and help options, opens the image and log, and calls `main_loop()`.
- `main_loop()` reads mixed request/reply/trace records from the transaction log.
- `process_command()` validates block alignment and applies supported commands.
- `dowriteimage()` writes a full buffer to the image at a given offset.
- `doread()` reads exact byte counts from the log.

## Control Flow
Replay requires an image path and log path. The default replay block size is 512 bytes; `-m` limits the number of blocks applied. Trace-log records toggle `g_with_datalog`; actual NBD writes can only be replayed when datalog was enabled in the trace. READ, DISC, and FLUSH are ignored. WRITE consumes logged data and writes it into the image block by block. TRIM and WRITE_ZEROES write zero-filled blocks over the target range.

## Dependencies
Uses POSIX `open`, `read`, and `pwrite`, plus local NBD protocol constants and helpers from `cliserv.h`, `nbd.h`, and `nbd-helper.h`.

## Risks and Notes
Replay operates at `g_blocksize` granularity and rejects unaligned offset/length values. It treats TRIM as zeroing, which may be useful for image reconstruction but does not preserve sparse/hole semantics. The log must contain datalog payloads for WRITE replay; otherwise the program exits.
