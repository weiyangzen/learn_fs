<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/profile.go -->
# sources/sync-backup/kopia/cli/profile.go

## Purpose
Implements runtime profiling flags for CPU, heap, goroutine, threadcreate, block, and mutex profile collection into diagnostics directories.

## Important APIs, Types, And Functions
Key symbols are `profileFlags`, `setup`, `start`, and `stop`. It uses Go `runtime` and `runtime/pprof` APIs and the shared `mkSubdirectories` helper.

## Control Flow
`start` applies requested profiling rates, enables sensible block/mutex defaults when saving profiles, creates the profile output directory, and starts CPU profiling if requested. `stop` closes CPU profiling, optionally forces GC, then writes all available pprof profiles to files.

## State And Persistence Behavior
Persistent output is profile files under `<diagnostics>/<run>/profiles`. Runtime-global profiling rates are changed for the process and not restored by this file.

## Dependencies And Integration Points
Integrates observability flag orchestration, diagnostics directory creation, Go runtime profiling, and CLI logging.

## Risks And Edge Cases
Changing runtime profiling rates is process-global and can affect concurrent in-process tests. CPU profile file creation failures abort command startup; non-CPU profile write failures are logged.

## Test Signals
Tests should cover directory creation, CPU profile start/stop, profile-store-on-exit outputs, GC-before-dump, and rate/fraction flag effects.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/profile.go -->
