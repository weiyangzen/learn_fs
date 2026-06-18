# sources/sync-backup/bup/dev/id-other-than

## Purpose
Finds a user or group ID/name different from excluded IDs/names for permission/ownership tests.

## Important APIs, Types, and Functions
Bootstraps `dev/bup-exec`, parses `--user` or `--group`, uses `pwd.getpwall`, `grp.getgrall`, `getpwnam`, and `getgrnam`.

## Control Flow
Builds an exclusion set from numeric arguments and resolved names, scans the user or group database, prints the first non-excluded `name:id`, and exits.

## State and Persistence Behavior
Read-only system account database access.

## Dependencies and Integration Points
Supports tests needing an alternate owner/group.

## Risks and Test Signals
Risks are systems with only excluded accounts or unresolved names. Signal is a valid `name:id` line or misuse exit.
