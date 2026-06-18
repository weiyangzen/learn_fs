## sources/sync-backup/restic/internal/global/global_release.go

Purpose: release-build stub for profiling registration.

Important APIs: `RegisterProfiling(_ *cobra.Command, _ io.Writer)` is a no-op under `!debug && !profile` build tags.

Control flow and state: no state and no side effects. It preserves the same API as `global_debug.go` so command initialization can call `RegisterProfiling` unconditionally.

Dependencies and integration points: imports only `io` and Cobra. Selected by Go build tags in normal releases.

Risks and test signals: risk is minimal; build-tag drift between debug and release files would cause compile errors. No direct tests are needed beyond normal release builds.
