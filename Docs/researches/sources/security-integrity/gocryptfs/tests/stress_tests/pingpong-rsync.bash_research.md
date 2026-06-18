# sources/security-integrity/gocryptfs/tests/stress_tests/pingpong-rsync.bash

## Purpose
Runs the shared ping-pong stress script in rsync mode, moving the Linux 3.0 tree between two gocryptfs mounts with `rsync --remove-source-files` and verifying MD5s each hop.

## Important APIs, Types, And Functions
- `MYNAME` basename selects rsync behavior inside `move_and_md5`.
- `move_and_md5` uses `rsync -a --remove-source-files`, deletes empty source dirs, and runs `md5sum --status -c`.

## Control Flow
The script initializes two independent gocryptfs cipherdirs, mounts them, extracts the tarball into the ping mount, then loops moving the tree ping-to-pong and pong-to-ping with checksum verification.

## State And Persistence
Creates two temp cipherdirs and mountpoints in `/tmp`, cleaned by an EXIT trap that tolerates already-unmounted FUSE mounts.

## Dependencies And Integration Points
Depends on rsync, gocryptfs, md5sum, tarball fixture, and `fuse-unmount.bash`.

## Risks And Edge Cases
Infinite loop by design; rsync semantics differ from `mv` and exercise remove-source and directory cleanup paths. Any leftover source directory is fatal.

## Test Signals
Continued numbered iterations with successful MD5 checks are the signal.
