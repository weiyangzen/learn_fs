# sources/sync-backup/bup/dev/unknown-owner

## Purpose
Generates a user or group name that should be unknown by making it longer than any existing account/group name.

## Important APIs, Types, and Functions
Bootstraps `dev/python`, parses `--user` or `--group`, uses `pwd.getpwall` or `grp.getgrall`.

## Control Flow
Computes maximum name length in the selected database and prints `x` repeated one more than that.

## State and Persistence Behavior
Read-only system account/group database query.

## Dependencies and Integration Points
Supports tests for unknown owner/group metadata handling.

## Risks and Test Signals
Risks include empty databases and systems permitting very long names. Signal is a likely-unknown name string.
