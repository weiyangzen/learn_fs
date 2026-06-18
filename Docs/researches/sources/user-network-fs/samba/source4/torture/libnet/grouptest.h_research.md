# sources/user-network-fs/samba/source4/torture/libnet/grouptest.h

## Purpose

`grouptest.h` defines the shared group name used by libnet group management tests.

## Important APIs, Types, and Functions

- `TEST_GROUPNAME` is defined as `libnetgrptest`.

## Control Flow

There is no control flow. Including files use the macro when creating and cleaning up temporary groups.

## State and Persistence Behavior

The header does not manage state. Its macro names a persistent directory object that tests may create and delete.

## Dependencies and Integration Points

It is included by `groupman.c` and can be used by other libnet group tests needing a common temporary group name.

## Risks and Edge Cases

Because this is a global test object name, concurrent tests or stale objects can collide. Changing the macro affects cleanup expectations across including tests.

## Test Signals

Build success confirms macro visibility. Runtime signals appear in group creation/cleanup tests that use this name.
