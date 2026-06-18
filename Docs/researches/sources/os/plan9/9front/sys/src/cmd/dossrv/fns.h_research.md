# File Research: sources/os/plan9/9front/sys/src/cmd/dossrv/fns.h

## Purpose
Shared function prototype header for `dossrv`.

## Key Contents
- Declares FAT parsing/debug helpers, cluster allocation/freeing, FAT read/write, directory search/name conversion, long-name handling, file read/write/truncate, contiguous-file support, time conversion, root/walk helpers, xfile/xfs management, sector/device I/O, 9P request handlers, locking, error/logging, and sync/cache functions.
- Includes `#pragma varargck` annotations for `chat()` and `panic()`.

## Notes
This header exposes almost the entire program as cross-file functions, matching the C style of the rest of the server.
