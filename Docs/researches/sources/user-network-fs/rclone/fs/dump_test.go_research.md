<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/dump_test.go -->
# sources/user-network-fs/rclone/fs/dump_test.go

## Purpose
Tests `DumpFlags` bitset parsing and rendering.

## Important APIs, Types, And Control Flow
Assertions cover empty and combined `String`, unknown bit rendering, comma-separated `Set`, invalid choice preservation of the previous value, `Type`, and JSON unmarshalling from strings and integers.

## State And Persistence
Local flag values only.

## Dependencies And Integration Points
Uses the generic `Bits` implementation through `DumpFlags`.

## Risks And Test Signals
Good coverage for CLI/JSON syntax. It does not test actual dump logging behavior; `fshttp/dump_test.go` covers part of that integration.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/dump_test.go -->
