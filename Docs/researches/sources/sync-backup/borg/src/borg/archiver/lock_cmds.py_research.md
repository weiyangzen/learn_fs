# sources/sync-backup/borg/src/borg/archiver/lock_cmds.py

## Purpose

`lock_cmds.py` implements repository lock utilities: `borg with-lock`, which runs a user command while holding the repository lock, and `borg break-lock`, which breaks repository and cache locks. The source was read as a complete 79-line file.

## Important APIs, Types, and Functions

`LocksMixIn.do_with_lock()` opens the repository exclusively without a manifest, starts a `ThreadRunner` that periodically calls `repository.info` to refresh the lock, runs a subprocess command, and sets Borg's exit code to the subprocess return code. `do_break_lock()` opens without taking a lock and calls `repository.break_lock()` plus `Cache.break_lock(repository)`. `build_parser_locks()` registers both commands and the `REMAINDER` argument for user command arguments.

## Control Flow

`with-lock` acquires the repository lock through the decorator, starts the refresh thread with a 60-second interval, prepares a system subprocess environment, executes `[args.command] + args.args`, records the return code, and terminates the refresh thread in `finally`. `break-lock` intentionally avoids acquiring the lock and directly removes lock state. Parser epilogs document intended cautious use.

## State and Persistence Behavior

`with-lock` creates and maintains a live repository lock while an arbitrary child process runs, then releases it through normal repository wrapper cleanup. It does not otherwise mutate the repository unless the child process does. `break-lock` mutates repository and cache lock files/state and can disrupt active Borg processes if misused.

## Dependencies and Integration Points

The module depends on repository locking from `with_repository`, cache lock handling, subprocess execution, `prepare_subprocess_env()`, `set_ec()`, `CommandError`, and `ThreadRunner`. It integrates with operational workflows such as copying repositories while locked.

## Risks and Edge Cases

The child command is arbitrary and inherits a Borg-prepared environment. If the command cannot execute, `CommandError` is raised. Lock refresh relies on `repository.info` as an indirect refresh mechanism because the repository API has no explicit refresh call. `break-lock` is dangerous on shared repositories and must only be used when no process is active.

## Test Signals

Tests should verify subprocess return code propagation, failed command errors, refresh-thread termination on success and failure, exclusive lock acquisition during command execution, and `break-lock` clearing both repository and cache lock fixtures.
