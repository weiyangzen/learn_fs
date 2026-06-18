# sources/sync-backup/kopia/internal/server/api_restore.go

Purpose: implements restore API as a background task with progress counters.

Important APIs/types/functions: `restoreCounters` and `handleRestore`.

Control flow: decodes restore request, resolves object/source/target parameters, starts a `uitask` restore operation, maps `restore.Stats` into UI counters, wires cancellation, and returns task metadata.

State and persistence behavior: reads repository object content and writes restored files to the local filesystem target; task manager records progress/logs.

Dependencies and integration points: integrates restore package, repository object lookup, server tasks, and UI APIs.

Risks and test signals: filesystem overwrite/safety options and cancellation are high risk. Tests cover restoring snapshots through the API and validating restored contents.
