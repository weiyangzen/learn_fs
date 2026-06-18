# File Research: sources/os/plan9/plan9/sys/src/cmd/dossrv/fns.h

Function prototype header for `dossrv`.

Key contents:
- Declares FAT parsing, boot dumps, allocation, FAT entry access, directory traversal, name conversion, file read/write/truncate, qid comparison, request handlers, cache sync, and server I/O functions.
- Declares diagnostics helpers `chat()` and `panic()` with Plan 9 vararg checking.
- Declares `xfile()`/`getxfs()` lifecycle APIs and `xerrstr()`.

Filesystem relevance:
- Captures the module boundary between 9P request handling, FAT metadata routines, cache/device I/O, and fid/backing-filesystem management.
