# sources/security-integrity/gocryptfs/tests/test_helpers/mount_unmount.go

## Purpose
Shared mount lifecycle utilities for gocryptfs tests. It starts the gocryptfs process, waits for readiness, records process file descriptors, unmounts with retries, and detects fd leaks.

## Important APIs, Types, And Functions
- `Mount` builds gocryptfs arguments, creates the mountpoint, starts `../../gocryptfs`, waits for SIGUSR1 readiness or process exit, and records mount info.
- `MountOrExit` and `MountOrFatal` adapt mount errors to process exit or test failure.
- `UnmountPanic` and `UnmountErr` run the FUSE unmount wrapper with retries and fd-leak checks.
- `ListFds` enumerates `/proc/<pid>/fd` or `/dev/fd`, filtering runtime pipes and eventpoll fds.

## Control Flow
Mounting starts gocryptfs foreground with quiet/no-syslog flags, Linux `-wpanic`, optional FUSE debug, and caller args. Unmounting waits for asynchronous close operations, compares fd counts allowing the frontend dir cache, then retries unmount up to ten times.

## State And Persistence
State is stored in global `MountInfo` keyed by mountpoint, containing the gocryptfs pid and baseline fd list.

## Dependencies And Integration Points
Depends on the gocryptfs binary, signal delivery, the `fuse-unmount.bash` wrapper, `/proc` for child fd inspection on Linux, and lsof for panic diagnostics.

## Risks And Edge Cases
Readiness relies on `-notifypid` SIGUSR1 within two seconds. FD leak checks allow `maxCacheFds` and filter runtime-created descriptors, so some leaks can be masked and some platform differences skipped.

## Test Signals
Signals are successful mount readiness, clean unmount, stable fd counts within cache allowance, and useful diagnostics on busy mounts.
