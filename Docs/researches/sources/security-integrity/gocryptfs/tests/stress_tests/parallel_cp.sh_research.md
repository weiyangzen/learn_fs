# sources/security-integrity/gocryptfs/tests/stress_tests/parallel_cp.sh

## Purpose
Reproducer for a historical parallel copy race where concurrent `cp` operations could fail with missing destination directories under gocryptfs.

## Important APIs, Types, And Functions
- Initializes a gocryptfs filesystem under `$TMPDIR` using `$GOPATH/bin/gocryptfs`.
- Creates 778 origin files with `dd`.
- Launches 100 background subshells that create subdirectories and copy the same origin file list.

## Control Flow
After mounting, the script precomputes `ORIGIN_FILES=origin/*`, then starts many concurrent mkdir/cp jobs. A final `wait` collects all background failures before cleanup.

## State And Persistence
Creates a temporary cipherdir and mountpoint, many files under the mount, and removes both on EXIT.

## Dependencies And Integration Points
Depends on Go GOPATH install of gocryptfs, dd, cp, seq, and the shared unmount helper.

## Risks And Edge Cases
It uses unquoted `$ORIGIN_FILES` intentionally for shell expansion captured once. The test is load-sensitive and may need cache-dropping pressure to reproduce old failures.

## Test Signals
A pass is all background copies completing and the script printing runtime without any `cp` or mkdir failure.
