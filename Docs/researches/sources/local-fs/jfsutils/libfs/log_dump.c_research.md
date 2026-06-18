# File Research: sources/local-fs/jfsutils/libfs/log_dump.c

## Purpose
Implements `jfs_logdump()`, a diagnostic dumper that opens a JFS journal log, validates the journal superblock, walks log records backward from the discovered end, and writes a human-readable dump to `./jfslog.dmp`.

## Main Flow
- `jfs_logdump(pathname, fp, dump_all)` opens the output file, calls `findLog()`, reads and swaps the journal superblock, prints superblock fields, warns on bad magic/version/redone state, calls `findEndOfLog()`, validates log-end bounds, and iterates log records with `logRead()`.
- Record types handled: `LOG_COMMIT`, `LOG_MOUNT`, `LOG_SYNCPT`, `LOG_REDOPAGE`, `LOG_NOREDOPAGE`, `LOG_NOREDOINOEXT`, `LOG_UPDATEMAP`, and unrecognized records.
- Stops at the last sync point unless `dump_all` requests the full valid chain.

## Helper Functions
- `ldmp_readSuper()`: reads primary superblock, falls back to secondary, then swaps.
- `ldmp_logError()`: reports log read/end/wrap errors and marks `logsup.state = LOGREADERR`.
- `ldmp_xdump()`, `ldmp_x_scmp()`, `ldmp_x_scpy()`: compact hex dump support.
- `disp_redopage()`, `disp_noredopage()`, `disp_noredoinoext()`, `disp_updatemap()`: decode log record payload descriptors.
- `open_outfile()`: opens `./jfslog.dmp`.

## Dependencies
Relies on global logredo state (`Log`, `logsup`, `afterdata`, `prog`, `retcode`), JFS log format definitions, endian helpers, `devices.h`, and `debug.h`.

## Notes
The output path is hard-coded. Error paths sometimes write to `outfp` after the file may have been closed in the normal loop-exit path, so this file is primarily diagnostic legacy code rather than a hardened library interface.
