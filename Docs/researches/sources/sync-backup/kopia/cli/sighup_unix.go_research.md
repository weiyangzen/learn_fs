<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/sighup_unix.go -->
# sources/sync-backup/kopia/cli/sighup_unix.go

## Purpose
Implements Unix external configuration reload handling by invoking a callback whenever SIGHUP is received.

## Important APIs, Types, And Functions
Defines `onExternalConfigReloadRequest` under `!windows`, creating a buffered signal channel with `signal.Notify(c, syscall.SIGHUP)` and a goroutine loop that calls the provided function on every signal.

## Control Flow
Once registered, the goroutine waits indefinitely and invokes the callback for each SIGHUP. Server start uses this to refresh server state.

## State And Persistence Behavior
No persistent state is changed. Runtime state is a signal subscription and goroutine for the process lifetime.

## Dependencies And Integration Points
Integrates Go signal handling and server refresh callback registration.

## Risks And Edge Cases
The signal subscription is never stopped, so repeated registrations can accumulate goroutines. Callback execution is synchronous inside the goroutine and can serialize or block future SIGHUP handling.

## Test Signals
Tests on Unix should send SIGHUP or use signal injection carefully; server refresh integration is the key behavioral signal.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/sighup_unix.go -->
