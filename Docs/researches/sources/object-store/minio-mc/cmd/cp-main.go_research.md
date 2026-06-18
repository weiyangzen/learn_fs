# sources/object-store/minio-mc/cmd/cp-main.go

Purpose: Implements `mc cp`, including flags, progress accounting, transfer scheduling, metadata/object-lock/tag/checksum setup, and move-mode hook support.

Important APIs/types/functions: `cpFlags`, `cpCmd`, `copyMessage`, `Progress`, `ProgressReader`, `doCopy`, `doCopyFake`, `printCopyURLsError`, `doCopySession`, `mainCopy`, and `doCopyOpts`.

Control flow: `mainCopy` validates syntax and encryption flags, then `doCopySession` prepares source/target URL pairs in one goroutine and schedules uploads through `newParallelManager` in another. It updates progress totals as objects are discovered, enriches `TargetContent` with storage class, retention, legal hold, tags, metadata, checksums, and multipart settings, then calls `uploadSourceToTargetURL` via `doCopy`.

State and persistence: Transfers data between local/object storage endpoints and may remove sources through `rmManager` when called for move. It does not persist local sessions in this file.

Dependencies/integration: Depends on copy URL preparation, encryption methods, progress bar/accounter, object lock checks, MinIO checksum types, upload helpers, and global cancellation.

Risks: `totalObjects`/`totalBytes` are shared between goroutines without synchronization. Error handling must coordinate channel closure, progress rollback, ignored errors, and cancellation. Metadata parsing error is discarded in the scheduling path after prior syntax validation assumptions.

Test signals: `cp-main_test.go` covers metadata parsing helper, not the transfer scheduler.
