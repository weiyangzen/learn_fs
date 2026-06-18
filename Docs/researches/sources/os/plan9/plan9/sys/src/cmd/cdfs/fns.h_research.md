# File Research: sources/os/plan9/plan9/sys/src/cmd/cdfs/fns.h

This header declares shared `cdfs` functions.

Key contents:
- Buffer APIs: `bopen()`, `bread()`, `bwrite()`, `bterm()`, `bufread()`, `bufwrite()`.
- Utility APIs: `emalloc()`, `geterrstr()`, `disctype()`.
- MMC probe entry point: `mmcprobe()`.

Filesystem relevance:
- Direct. Declares the cross-file APIs for the `cdfs` 9P service and MMC driver.
