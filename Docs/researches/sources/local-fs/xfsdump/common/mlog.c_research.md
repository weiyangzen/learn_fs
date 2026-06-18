# File Research: sources/local-fs/xfsdump/common/mlog.c

## Role

This file implements xfsdump/xfsrestore message logging, verbosity parsing, thread-aware log prefixes, structured exit recording, and final dump/restore status summaries.

It is shared by dump and restore builds.

## Initialization

`mlog_init0()` chooses the default output stream and initializes all subsystem verbosity levels to verbose.

`mlog_init1()` parses verbosity-related options:

- general or per-subsystem verbosity through `GETOPT_VERBOSITY`
- show log level
- show log subsystem
- timestamp messages

It supports numeric and symbolic levels: silent, verbose, trace, debug, and nitty.

`mlog_init2()` allocates the ordered `QLOCK_ORD_MLOG` lock.

## Logging Behavior

`mlog()` wraps `mlog_va()`. `mlog_va()`:

- Extracts message level and subsystem.
- Filters messages above the configured subsystem level.
- Optionally locks the mlog qlock.
- Prints prefixes including program name, optional timestamp, subsystem, level, and stream/drive index when applicable.
- Adds NOTE, WARNING, or ERROR labels when requested.
- Writes the formatted message and flushes the log file.

`MLOG_NOLOCK` is supported for contexts where locking is unsafe or already protected.

## Subsystems

The file defines names for general, process, drive, media, inventory, dump inomap or restore tree, and excluded files. The exact fifth subsystem depends on build mode.

## Exit Recording

`mlog_exit()` and `mlog_exit_hint()` are implemented through file/line-aware macros. They record:

- traditional exit code
- internal `rv_t` reason code
- optional late hint reason

The parent thread stores process-level exit data. Worker/content threads store exit status through the `stream` subsystem.

The first exit value is preserved because deeper callers often have the most specific reason. Hints use the last value because they are intended to improve final diagnosis near the final failure point.

## Return-Code Mapping

The file maps every `rv_t` value to a displayed code and human-readable description, including media, drive, corruption, interrupt, incomplete, permission, compatibility, inventory, and usage conditions.

## Final Summary

`mlog_exit_flush()` emits final per-stream and overall status unless logging is silent or the run only printed usage. It scans running/zombie streams, combines each stream's return and hint, reports drive path and reason, and derives an overall status such as INTERRUPT, QUIT, INCOMPLETE, or the traditional exit-code string.

## Utility

`fold_init()` builds fixed-width fold/separator strings used by the interrupt dialog.
