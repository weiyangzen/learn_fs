# sources/security-integrity/gocryptfs/tests/reverse/one_file_system_test.go

## Purpose
Tests reverse-mode `-one-file-system` behavior on Linux by mounting `/` and ensuring cross-device mountpoints are hidden except for expected virtual entries.

## Important APIs, Types, And Functions
- `TestOneFileSystem` identifies top-level directories whose inode numbers were remapped above the passthrough range, then attempts to read them.

## Control Flow
The test mounts `/` with `-reverse -zerokey -one-file-system`, scans top-level entries, treats high inode numbers as mountpoints from other devices, and verifies their directory listings are empty or contain only `gocryptfs.diriv` depending on mode.

## State And Persistence
State is a temporary reverse mount of `/`; it reads host root metadata but does not modify it.

## Dependencies And Integration Points
Depends on Linux, reverse mode flags, `test_helpers`, and inode range assumptions copied from inomap.

## Risks And Edge Cases
It skips on non-Linux and when no mountpoints are found. Host root layout affects how much coverage is achieved.

## Test Signals
Pass signal is every detected cross-device mountpoint exposing only the expected number of entries.
