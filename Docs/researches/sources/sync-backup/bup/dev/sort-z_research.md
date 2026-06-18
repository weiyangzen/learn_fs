# sources/sync-backup/bup/dev/sort-z

## Purpose
Portable null-delimited sort wrapper.

## Important APIs, Types, and Functions
Uses `sort -z` normally and `sort -R 000` on NetBSD.

## Control Flow
Checks `uname -s`; execs the appropriate sort command with original args.

## State and Persistence Behavior
No persistence; transforms stdin/files according to sort.

## Dependencies and Integration Points
Used by tests/scripts requiring NUL-delimited sorting across platforms.

## Risks and Test Signals
Risk is NetBSD option compatibility and differing sort collation. Signal is sorted NUL-delimited output.
