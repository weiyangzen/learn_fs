# Research: sources/object-store/minio-mc/cmd/ilm-restore.go

Purpose: implements `mc ilm restore`, restoring archived objects from remote tier back to hot storage for a limited number of days.

Important APIs/types/functions: `ilmRestoreFlags`, `checkILMRestoreSyntax`, `restoreObject`, `sendRestoreRequests`, `waitRestoreObject`, `checkRestoreStatus`, `showRestoreStatus`, and `mainILMRestore`.

Control flow: validates one target, positive `--days`, and incompatible version flags. For a single object it sends one restore request; for recursive mode it lists objects, optionally with versions, and sends restore calls per content. It then polls `Stat` until restore is no longer ongoing, showing progress or JSON summary.

State and persistence: sends S3 restore requests, creating temporary restored copies server-side. Does not persist local state.

Dependencies/integration points: MinIO client `Restore`, `List`, and `Stat`; SSE-C parsing through `validateAndCreateEncryptionKeys` and `getSSE`.

Risks: polling loops have no timeout beyond process cancellation. Recursive restore can issue many requests and waits sequentially during status checks. Version syntax check incorrectly uses `ctx.Bool("version-id")` for a string flag, which should be reviewed.

Test signals: no direct tests; should cover syntax matrix, recursive list behavior, SSE-C stat options, and JSON progress output.
