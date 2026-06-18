# sources/sync-backup/restic/internal/fs/fs_track.go

Purpose: Debug wrapper that detects leaked open `File` handles.

Important APIs: `Track.OpenFile`, `trackFile`, `newTrackFile`, and `trackFile.Close`.

Control flow and state: `OpenFile` delegates to an underlying `FS`, captures a stack trace, and wraps the result in a `trackFile` with a finalizer. If garbage collection releases the wrapper before `Close`, the finalizer prints the opening stack and panics. `Close` clears the finalizer and closes the underlying file.

Dependencies and integration: Uses `runtime.SetFinalizer` and `runtime/debug.Stack`. Can wrap any `FS` implementation during tests or debugging.

Risks: Finalizer-based checks are nondeterministic and should not be part of normal runtime behavior. Panic on leaked file is intentional but disruptive.

Test signals: No direct tests in this subset; leaks are observable when wrapper is enabled.
