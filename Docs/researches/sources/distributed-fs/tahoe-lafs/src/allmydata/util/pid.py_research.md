# sources/distributed-fs/tahoe-lafs/src/allmydata/util/pid.py

## Purpose

This module manages Tahoe pidfiles with file locking and process checks. It prevents multiple instances from using the same pidfile and cleans stale pidfiles when their process no longer exists.

## APIs and control flow

`_pidfile_to_lockpath()` maps `node.pid` to a sibling lock path. `parse_pidfile()` reads `pid starttime` and raises `InvalidPidFile` on malformed content. `check_pid_process()` locks the pidfile, checks an existing pid with psutil, raises `ProcessInTheWay` if any process currently owns that PID, removes stale pidfiles for missing processes, then writes the current process PID and creation time. Lock timeout also maps to `ProcessInTheWay`. `cleanup_pidfile()` locks and removes the file, wrapping failures in `CannotRemovePidFile`.

## State, dependencies, risks, and tests

Persistent state is the pidfile and lock file. Dependencies are `psutil`, `filelock`, and Twisted `FilePath`-like methods (`sibling`, `basename`, `open`, `exists`, `remove`, `path`).

Risks include only checking PID existence during `check_pid_process()` rather than comparing saved start time, stale lock files, removal failure, and process creation time precision differences across platforms. Test signals should cover malformed files, stale PID cleanup, live PID conflict, lock timeout, pidfile write format, cleanup success/failure, and PID reuse scenarios for automated callers that inspect start time.
