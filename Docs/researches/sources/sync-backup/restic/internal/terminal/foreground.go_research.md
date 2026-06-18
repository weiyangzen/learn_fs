<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/terminal/foreground.go -->
# sources/sync-backup/restic/internal/terminal/foreground.go

## Purpose
Provides the public entry point for running an external command in the foreground while scrubbing restic secrets from the environment.

## Important APIs and Control Flow
`StartForeground` removes all `RESTIC_*` variables from `cmd.Env` and delegates to platform-specific `startForeground`. Control flow copies `os.Environ`, filters sensitive variables, then starts foreground handling.

## State, Persistence, Dependencies, and Integration
State mutation is limited to the supplied `exec.Cmd`. Integration points are backend commands that need terminal foreground control and safe environment inheritance.

## Risks and Test Signals
Risks are missed secret environment prefixes and platform-specific foreground failures. Tests verify `RESTIC_PASSWORD` is not visible to a subprocess.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/terminal/foreground.go -->
