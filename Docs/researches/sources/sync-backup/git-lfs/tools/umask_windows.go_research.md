# sources/sync-backup/git-lfs/tools/umask_windows.go

Purpose: Windows no-op implementation of temporary umask wrapper.

Important APIs/types/functions: `doWithUmask`.

Control flow: immediately calls the supplied function.

State and persistence: no umask state on Windows.

Dependencies and integration points: lets shared `Mkdir`/`MkdirAll` compile cross-platform.

Risks: Windows permissions do not mirror Unix umask semantics.

Test signals: write-flag tests include Windows-specific expectations.
