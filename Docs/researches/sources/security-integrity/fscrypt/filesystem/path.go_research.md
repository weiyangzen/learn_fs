# sources/security-integrity/fscrypt/filesystem/path.go

## Purpose
`path.go` provides low-level path, stat, access, and device-number helpers used by filesystem setup and mount discovery.

## Important APIs, Types, and Functions
`OpenFileOverridingUmask` creates files with exact permissions. `canonicalizePath`, `loggedStat`, `loggedLstat`, `isDir`, `isRegularFile`, and `HaveReadAccessTo` wrap common filesystem checks. `DeviceNumber` represents combined major/minor device numbers, with `String`, `newDeviceNumberFromString`, `getDeviceNumber`, and `getNumberOfContainingDevice`.

## Control Flow
The helpers are direct wrappers around `filepath.Abs`, `filepath.EvalSymlinks`, `os.Stat`, `os.Lstat`, `unix.Access`, `unix.Stat`, and `unix.Lstat`. Device parsing uses `fmt.Sscanf`, and formatting uses `unix.Major`/`unix.Minor`.

## State and Persistence
No persistent state is maintained. `OpenFileOverridingUmask` temporarily changes the process umask and restores it with `defer`, which is process-global state during the call.

## Dependencies and Integration Points
Used by mountpoint parsing for device matching and directory filtering, and by filesystem metadata setup for safe stat behavior. It depends on `golang.org/x/sys/unix` and `github.com/pkg/errors`.

## Risks
Changing umask is process-global and can affect concurrent file creation in other goroutines during the small critical section. `HaveReadAccessTo` reports kernel access checks without opening the file, so callers still need race-safe open logic for security-sensitive reads.

## Test Signals
`path_test.go` validates `/dev/null` device formatting/parsing, invalid device strings, nonexistent device errors, and read-access checks for non-root users across permission modes.
