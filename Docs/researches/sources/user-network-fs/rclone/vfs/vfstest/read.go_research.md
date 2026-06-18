# sources/user-network-fs/rclone/vfs/vfstest/read.go

## Purpose
Contains shared functional read tests for byte-wise reads, checksum behavior, and seeking.

## APIs, Flow, And State
`TestReadByByte` repeatedly opens a file and reads increasing prefixes one byte at a time. `TestReadChecksum` reads a large file fully enough and partially enough to exercise checksum comparison decisions on close. `TestReadSeek` verifies reads after seeks to middle, end, beyond end, and back to start.

## Dependencies And Integration
Uses the `run` harness for file creation, opening, reading, and cleanup. It validates read handle behavior across cache modes and mount/direct VFS operation.

## Risks And Test Signals
Failures point to broken sequential offsets, EOF behavior, seek handling, or checksum-trigger conditions. Tests are intentionally black-box from the mounted/VFS API surface.
