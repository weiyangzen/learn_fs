# sources/security-integrity/gocryptfs/tests/stress_tests/fsstress-loopback.bash

## Purpose
Runs the shared fsstress loop in `go-fuse loopback` mode to repeatedly exercise high-concurrency filesystem mutations against a mounted filesystem until an error occurs.

## Important APIs, Types, And Functions
- `TMPDIR` defaults to `/var/tmp`; `DEBUG` toggles FUSE or loopback debug mode.
- `FSSTRESS=/var/lib/xfstests/ltp/fsstress` is required.
- Mode selection is inferred from the script basename and chooses gocryptfs, EncFS, or go-fuse loopback mounting.

## Control Flow
The script creates a backing directory and mountpoint, cleans stale mounts matching its temp prefix, mounts the selected filesystem, waits for a FUSE mount entry, and loops through three fsstress profiles followed by recursive cleanup of the mount contents.

## State And Persistence
It creates and removes temporary backing and mount directories, keeps the selected filesystem mounted for the process lifetime, and may leave artifacts if the trap is bypassed by abrupt termination.

## Dependencies And Integration Points
Depends on xfstests `fsstress`, Go/GOPATH for gocryptfs or loopback modes, EncFS for EncFS mode, `/proc/self/mounts`, and the shared `fuse-unmount.bash` helper.

## Risks And Edge Cases
The loop is intentionally unbounded and destructive inside its temp tree. The cleanup trap uses `kill %1`, so job-control assumptions matter. Running with `DEBUG=1` can generate large logs.

## Test Signals
The only pass signal is continued iteration. Any fsstress, rm, mount, or unmount failure exits because `set -eu` is active.
