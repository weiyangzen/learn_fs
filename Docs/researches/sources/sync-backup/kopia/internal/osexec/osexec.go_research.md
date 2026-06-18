# sources/sync-backup/kopia/internal/osexec/osexec.go

Purpose: package anchor for OS-specific command execution helpers.

Important APIs/types/functions: the portable API is supplied by build-tagged `DisableInterruptSignal` implementations.

Control flow: no executable logic in this file.

State and persistence behavior: no state.

Dependencies and integration points: package is imported where Kopia starts child processes and needs platform-specific signal behavior.

Risks and test signals: build tags must always provide exactly one implementation for target OSes.
