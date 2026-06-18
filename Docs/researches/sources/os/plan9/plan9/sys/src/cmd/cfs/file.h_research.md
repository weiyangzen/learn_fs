# File Research: sources/os/plan9/plan9/sys/src/cmd/cfs/file.h

This header declares cached file-data operations for `cfs`.

Key contents:
- `fmerge()`
- `fbwrite()`
- `fwrite()`
- `fpget()`
- `fread()`

Filesystem relevance:
- Direct. Exposes file-range cache operations to the 9P proxy.
