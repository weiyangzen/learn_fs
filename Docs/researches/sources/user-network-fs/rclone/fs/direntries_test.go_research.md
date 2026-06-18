<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/direntries_test.go -->
# sources/user-network-fs/rclone/fs/direntries_test.go

## Purpose
Tests `DirEntries` sort ordering.

## Important APIs, Types, And Control Flow
Creates mock objects and directories with names `a`, `b`, and `c`, sorts stably, and expects directories before objects for equal remote names while preserving duplicate object order.

## State And Persistence
No persistence; local mock entries only.

## Dependencies And Integration Points
Uses `fstest/mockdir`, `fstest/mockobject`, standard `sort`, and testify.

## Risks And Test Signals
Focused signal for ordering. It does not cover callback helper methods or unknown entry classification.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/direntries_test.go -->
