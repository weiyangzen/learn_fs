# File Research: sources/local-fs/xfsprogs/db/output.c

## Purpose
Centralizes xfs_db formatted output and optional command/output logging.

## Main Interfaces
- Registers `log` through `output_init()`.
- Exports `dbprintf()`, `logprintf()`, and global `dbprefix`.
- `log [stop|start <filename>]` reports, starts, or stops logging.

## Control Flow
`dbprintf()` suppresses output during interrupt handling, blocks interrupts while printing, optionally prefixes output with the data device name, writes to stdout, and mirrors to the log file when active. `logprintf()` writes only to the log file. `log_f()` manages log file open/close state.

## Dependencies
Uses signal masking helpers, malloc wrappers, global libxfs init state for the prefix, and stdio.

## Risks And Invariants
- Logging is append-only.
- The `log start` path stores `argv[1]` as `log_file_name`, which is the literal command word `"start"` rather than the filename; status output can therefore be misleading.
