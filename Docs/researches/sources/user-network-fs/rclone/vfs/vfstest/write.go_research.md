# sources/user-network-fs/rclone/vfs/vfstest/write.go

## Purpose
Contains shared functional write tests for creates, overwrites, fsync, duplicate descriptors, and append mode.

## APIs, Flow, And State
Tests cover closing a created file without writes, writing and reading back data, overwriting, syncing before close, duplicated writer file descriptors, and `O_APPEND` in cache modes that support writes. Dup and append cases are skipped where platform or cache mode cannot support them.

## Dependencies And Integration
Uses `osCreate`, `osAppend`, `writeTestDup`, `run.waitForWriters`, cache-mode options, and mounted/direct filesystem operations from the harness.

## Risks And Test Signals
These tests expose writeback timing, flush/release behavior, cache-mode restrictions, append handling, and duplicate-fd semantics. One open-file listing test is disabled as `FIXME`.
