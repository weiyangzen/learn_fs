# sources/security-integrity/gocryptfs/tests/sshfs-benchmark.bash

## Purpose
Ad hoc benchmark comparing basic operations on raw sshfs versus gocryptfs layered on sshfs.

## Important APIs, Types, And Functions
- `prepare_mounts` mounts `$HOST:/tmp` via sshfs, creates a remote-backed cipherdir, initializes gocryptfs, and mounts it locally.
- `etime` wraps `/usr/bin/time -f %e` and prints aligned elapsed seconds.
- `cleanup` unmounts both FUSE layers and removes temp dirs.

## Control Flow
The script takes a host argument, prepares sshfs and gocryptfs-on-sshfs mounts, then times `git init`, `rsync`, recursive remove, mkdir/rmdir, touch, and rm on both paths.

## State And Persistence
Creates local temp dirs, a remote temp dir under sshfs, and two FUSE mounts. Cleanup is registered after sshfs mount setup.

## Dependencies And Integration Points
Depends on sshfs, gocryptfs, git, rsync, `/usr/bin/time`, fusermount, and passwordless or interactive SSH access to the host.

## Risks And Edge Cases
The script assumes `$1` is present and uses unquoted generated `seq` arguments intentionally. Network latency and remote `/tmp` filesystem dominate results.

## Test Signals
Output table of elapsed seconds is the benchmark signal; any command failure exits due to `set -eu`.
