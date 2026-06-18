# sources/security-integrity/gocryptfs/tests/matrix/matrix_test.go

## Purpose
Contains the bulk of forward-mode filesystem behavior tests for gocryptfs. It verifies data integrity, truncation, sparse files, name encryption, long names, metadata operations, timestamps, special files, permissions, sizing, and rename exchange.

## Important APIs, Types, And Functions
- `testWriteN` writes deterministic random-sized payloads and verifies size plus MD5.
- `TestWrite10`, `TestWrite100`, `TestWrite1M`, `TestWrite100x100`, and `TestWrite10Tight` cover repeated file I/O.
- `TestTruncate`, `TestAppend`, `TestFileHoles`, and `TestRmwRace` stress content size, sparse, append, and concurrent read-modify-write paths.
- `TestFiltered`, `TestFilenameEncryption`, `TestNameLengths`, `TestLongNames`, `TestLongLink`, and `TestMagicNames` cover name translation edge cases.
- `doTestUtimesNano`, `TestUtimesNano`, `TestUtimesNanoFd`, `TestUtimesNanoSymlink`, `TestChmod`, `TestAccess`, `TestStatfs`, `TestSymlinkSize`, `TestLinkSize`, `TestDirSize`, and `TestRenameExchangeOnGocryptfs` cover metadata and syscall behavior.

## Control Flow
Each test operates under the active mount created by `matrix/main_test.go`. Data-path tests create files under `DefaultPlainDir`, verify plaintext results, and sometimes inspect `DefaultCipherDir` or the control socket to reason about encrypted names. Metadata tests call low-level syscalls directly to catch FUSE/kernel contract regressions.

## State And Persistence
State is mostly temporary filesystem state in the mounted gocryptfs tree. Some tests intentionally create long-name helper files, special names, FIFOs, symlinks, hard links, and nested directories, then remove them or compare final cipherdir entry counts.

## Dependencies And Integration Points
Depends on Go `os`, `syscall`, `golang.org/x/sys/unix`, `internal/syscallcompat`, `ctlsock`, and shared helpers for MD5, size checks, rename checks, and control-socket queries.

## Risks And Edge Cases
The file contains mode-sensitive expectations for `-plaintextnames`, long-name virtual files, raw64, deterministic names, and Darwin timestamp limitations. `TestRmwRace` records acceptable hashes but does not assert the map contents, so it is mainly a race reproducer scaffold.

## Test Signals
Strong signals include fixed MD5s after truncation, size agreement between read/stat/fstat, successful long-name create/rename/unlink cycles without cipherdir leaks, correct symlink and hardlink sizes, and successful `RENAME_EXCHANGE` content swap.
