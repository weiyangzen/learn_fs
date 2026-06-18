# File Research: sources/os/bsd/freebsd-src/sbin/ddb/ddb.c

## Purpose
Top-level command dispatcher for managing DDB capture buffers and scripts.

## Main Elements
- `usage()`: documents `capture`, `script`, `scripts`, `unscript`, and pathname modes.
- `ddb_readfile()`: reads a config file, skips blanks/comments, splits each line into command plus optional argument string, and dispatches it.
- `ddb_main()`: dispatches subcommands.
- `main()`: treats a single readable absolute path as a batch file; otherwise dispatches command-line arguments.

## Dependencies And Integration
Calls functions declared in `ddb.h` and implemented by `ddb_capture.c` and `ddb_script.c`.

## Risk Notes
Batch parsing supports only two logical arguments per line: command and the rest of the line.
