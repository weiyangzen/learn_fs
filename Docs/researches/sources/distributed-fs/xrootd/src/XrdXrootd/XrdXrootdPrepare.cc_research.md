# sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdPrepare.cc

## Purpose

This file implements persistent logging for xroot `prepare` requests. It records request metadata and path lists as files in a configured directory, supports listing/opening/deleting those records, and periodically scrubs stale entries.

## Important APIs, types, and functions

`XrdXrootdPrepare::List()` iterates log files matching optional request id and user filters. `Log()` writes a prepare record named `<reqid>_<user>_<priority>_<numpaths>` and creates a symlink named `<reqid>`. `Logdel()` removes the symlink target and symlink. `Open()` opens a request id symlink and returns its size. `Scrub()` deletes stale records. `setParms()` configures scrub timing and log directory.

## Control flow

The constructor stores the scheduler/logger and schedules the scrub job when `LogDir` is configured. `DoIt()` calls `Scrub()` and reschedules itself. Request execution code builds `XrdXrootdPrepArgs`, calls `Log()` for tracked prepares, `List()` for query-style enumeration, and `Logdel()` for cancellation/removal.

## State and persistence behavior

Static process state includes `scrubtime`, `scrubkeep`, `LogDir`, and `LogDirLen`. Durable state is the prepare log directory: one data file per request and one request-id symlink. The file body stores paths separated by spaces with a final newline; metadata is encoded in the filename.

## Dependencies and integration points

The file uses POSIX directory, file, symlink, stat, and `writev` APIs. It integrates with `XrdScheduler` as an `XrdJob`, `XrdSysError` for diagnostics, `XrdOucTList` path lists, and protocol prepare/query handlers in `XrdXrootdXeq.cc`.

## Risks and edge cases

Filename construction trusts `reqid` and `user` strings supplied by callers; those must already be sanitized to avoid path separators or excessive length. `List()` mutates `dirent->d_name` by replacing underscores with spaces, which is common on mutable `dirent` buffers but is still a fragile parsing style. `Scrub()` uses underscore presence to identify records and may skip malformed files. `getUTC` is unrelated; all timestamps here use filesystem `mtime`.

## Test signals

Tests should cover directory validation, file/symlink creation, listing by request/user, deletion when either file or symlink is missing, stale scrub behavior, long request id rejection in `Logdel()`, and behavior when logging is disabled.
