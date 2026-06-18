# sources/security-integrity/gocryptfs/tests/reverse/correctness_test.go

## Purpose
Exercises reverse-mode correctness through a normal directory, a reverse encrypted view, and a forward mount of that encrypted view. It focuses on virtual files, symlinks, long names, access checks, sparse seeking, inode reuse, and timestamp nudging.

## Important APIs, Types, And Functions
- `TestLongnameStat`, `TestSymlinks`, `TestSymlinkDentrySize`, and `TestConfigMapping` verify reverse presentation of names, symlinks, and config mapping.
- `TestAccessVirtualDirIV`, `TestAccess`, `TestEnoent`, `TestTooLongSymlink`, `Test0100Dir`, `TestStatfs`, and `TestSeekData` cover syscall semantics.
- `newWorkdir` maps plaintext workdirs to encrypted paths by inode.
- `TestHardlinkedLongname` and `TestMtimePlus10` protect virtual longname and diriv inode/cache behavior.

## Control Flow
Tests create source files in `dirA`, observe encrypted names in `dirB`, and often verify decrypted content through `dirC`. Control socket queries and inode matching bridge plaintext and encrypted views for long-name and virtual-file assertions.

## State And Persistence
State spans all three package global dirs initialized by reverse `TestMain`. Some tests move or rename files instead of unlinking to avoid immediate ext4 inode reuse side effects.

## Dependencies And Integration Points
Depends on `ctlsock`, `internal/syscallcompat`, `golang.org/x/sys/unix`, shared helper functions, and the reverse package globals `plaintextnames`, `deterministic_names`, `dirA`, `dirB`, and `dirC`.

## Risks And Edge Cases
Many expectations are mode-sensitive: plaintextnames and deterministic names skip virtual diriv or longname assertions. Long symlink limits vary by backing filesystem.

## Test Signals
Signals include readable forward-remounted content, correct virtual config and diriv behavior, expected `ENOENT`/`ENAMETOOLONG`, successful traversal of execute-only dirs, preserved SEEK_DATA behavior in plaintextnames mode, distinct `.name` inodes, and mtime+10 for virtual files.
