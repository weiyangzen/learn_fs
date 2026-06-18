# sources/security-integrity/gocryptfs/tests/reverse/inomap_test.go

## Purpose
Validates inode mapping for reverse-mode passthrough files and virtual files such as `gocryptfs.diriv` and longname `.name` helpers.

## Important APIs, Types, And Functions
- `findIno` scans a directory for an entry with a requested inode.
- `TestVirtualFileIno` compares original parent/child inodes with encrypted parent, diriv, child, and `.name` inodes.

## Control Flow
The test creates a parent directory and a long-name child, records source inodes, locates the encrypted parent by inode in `dirB`, enumerates its entries, classifies virtual and real entries, and applies collision and high-bit spill-space checks.

## State And Persistence
State is a generated directory tree under `dirA` and corresponding virtual entries under `dirB`. No durable state escapes the reverse test temp dirs.

## Dependencies And Integration Points
Depends on reverse globals, direct `syscall.Lstat`, and directory enumeration. It shares `findIno` with `correctness_test.go` through package scope.

## Risks And Edge Cases
Plaintextnames mode has no virtual files and is skipped. Deterministic names suppress diriv checks. The test encodes assumptions about lower 48-bit passthrough inode space and high spill-space allocation.

## Test Signals
Signals include matching parent and child passthrough inodes, no collisions with diriv or `.name`, lower-bit diriv derivation when applicable, and `.name` inode above `1<<63`.
