# sources/storage-engines/wiredtiger/test/thread/smoke.sh

## Purpose

`smoke.sh` is the CTest smoke driver for the thread stress executable.

## Important APIs, Types, and Functions

It is a POSIX shell script with `set -e` and four `$TEST_WRAPPER ./t ...` invocations.

## Control Flow

The script runs row-store mode, row-store mode with per-operation sessions and multiple files, variable-record mode, and variable-record mode with per-operation sessions and multiple files. Any command failure stops the script.

## State and Persistence Behavior

Each `t` invocation creates and removes its own WiredTiger work directory according to executable defaults.

## Dependencies and Integration Points

Depends on the built binary being named `t`, optional `TEST_WRAPPER`, and command-line options implemented by `t.c`.

## Risks and Edge Cases

It is intentionally small and only exercises reduced operation counts for the `-S -F -n 1000` variants. Environment must provide `TEST_WRAPPER` or allow it to expand empty.

## Test Signals

Signals are zero exit from all four stress invocations.
