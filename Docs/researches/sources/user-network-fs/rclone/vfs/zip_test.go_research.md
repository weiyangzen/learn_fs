# sources/user-network-fs/rclone/vfs/zip_test.go

## Purpose
Tests ZIP creation from VFS directories for flat files, nested directories, large content, and root children.

## APIs, Flow, And State
Helpers create ZIP buffers, read them with `archive/zip`, and locate file entries by predicate. Tests write objects to a test remote, stat directories through VFS, call `CreateZip`, count file entries, and verify contents or SHA-256 checksum.

## Dependencies And Integration
Uses `newTestVFS`, `fstest`, random data, and VFS directory nodes. A chunker backend skip avoids an overly slow large-file case.

## Risks And Test Signals
The tests are content-oriented and deliberately tolerant of directory-entry naming by matching suffixes. They give signal for recursive traversal and streaming integrity but do not check every ZIP metadata field.
