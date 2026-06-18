# sources/sync-backup/syncthing/internal/slogutil/recorder.go

Purpose: Bounded in-memory log recorder.

Important APIs/types/functions: `Recorder` exposes `Since(time.Time) []Line` and `Clear()`. `NewRecorder(level slog.Level)` returns a `lineRecorder`. `lineRecorder.record` filters below its level, appends lines, and retains only the newest `maxLogLines` entries.

Control flow: All mutations and reads are protected by a mutex. `Since` scans from oldest to newest and returns a slice starting at the first line whose timestamp is after the supplied time.

State and persistence behavior: Keeps up to 1000 `Line` values in memory. `Clear` drops the buffer. The returned slice aliases internal storage, so callers should treat it as read-only.

Dependencies and integration points: Global and error recorders are wired in `sloginit.go`; API endpoints and support bundles read from them.

Risks: Returning an internal slice after unlocking can expose races if callers mutate it or if later appends re-use storage. Bounded retention means older log data disappears from API responses.

Test signals: No direct tests in this subset; API log and support bundle tests exercise read paths indirectly.
