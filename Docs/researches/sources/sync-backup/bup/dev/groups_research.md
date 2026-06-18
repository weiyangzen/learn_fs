# sources/sync-backup/bup/dev/groups

## Purpose
Prints current process group names, including the effective gid when `os.getgroups()` omits it.

## Important APIs, Types, and Functions
Bootstraps `dev/python`; uses `os.getegid`, `os.getgroups`, and `grp.getgrgid`.

## Control Flow
Collects groups, appends egid if missing, resolves group names, and prints them space-separated.

## State and Persistence Behavior
No persistence; reads process credentials and system group database.

## Dependencies and Integration Points
Parallels `helpers.getgroups()` behavior for test/dev scripts.

## Risks and Test Signals
Risks are unknown gids raising and platform group semantics. Signal is group-name output matching process membership.
