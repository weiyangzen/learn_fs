<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/deletemode.go -->
# sources/user-network-fs/rclone/fs/deletemode.go

## Purpose
Defines delete timing constants for sync/delete operations.

## Important APIs, Types, And Control Flow
`DeleteMode` is a byte enum with values off, before, during, after, only, and default after. This file contains only the type and constants; parsing/string behavior likely lives elsewhere or through option metadata.

## State And Persistence
Pure constants, no state.

## Dependencies And Integration Points
Consumed by higher-level operations and config options controlling when destination deletions occur.

## Risks And Test Signals
Numeric ordering is compatibility-sensitive. No direct tests in this subset, so behavior relies on consumers and option parsing tests elsewhere.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/deletemode.go -->
