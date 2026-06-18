# sources/security-integrity/gocryptfs/tests/stress_tests/extractloop.bash

## Purpose
Long-running stress loop that repeatedly extracts and deletes the Linux 3.0 tree through gocryptfs, EncFS, or go-fuse loopback while optionally recording memory and iteration time.

## Important APIs, Types, And Functions
- `check_md5sums` verifies extracted contents when `md5sum` is available.
- `cleanup_exit` tears down mounts and, for loopback, triggers memory profile output.
- `loop` performs extract, checksum, delete, and CSV metric append for one worker.
- `memprof` periodically signals loopback for memory profiles.

## Control Flow
The script prepares a temp cipherdir and mountpoint, selects filesystem mode from arguments, mounts it, symlinks the CSV to `/tmp/extractloop.csv`, then launches two infinite loop workers. Each worker extracts the tarball, verifies checksums, removes the tree, records RSS and duration if possible, and repeats.

## State And Persistence
Persistent runtime artifacts include temp backing and mount dirs, CSV metrics, and optional `/tmp/loopback*.memprof` files. Cleanup removes the backing tree and mountpoint.

## Dependencies And Integration Points
Depends on Linux tarball download helper, tar, md5sum or macOS fallback, gocryptfs/encfs/loopback binaries, `/proc` for RSS, and `fuse-unmount.bash`.

## Risks And Edge Cases
It is intentionally unbounded and creates huge file churn. Running on non-Linux skips checksum if `md5sum` is absent, reducing integrity signal.

## Test Signals
Continued iterations with stable checksum validation and bounded RSS in the CSV are the main signals.
