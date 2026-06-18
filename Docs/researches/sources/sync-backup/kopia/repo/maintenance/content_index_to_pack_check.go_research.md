# sources/sync-backup/kopia/repo/maintenance/content_index_to_pack_check.go

Purpose: optionally verifies that content index entries point to readable pack blobs before and after selected maintenance tasks.

Important APIs/types/functions: `checkContentIndexToPacks`, `shouldRunContentIndexVerify`, and `reportRunAndMaybeCheckContentIndex`.

Control flow: verification walks all contents with fixed parallelism and calls `VerifyContent`. The environment variable `KOPIA_MAINTENANCE_CONTENT_VERIFY_PERCENTAGE` controls whether a random percentage gate enables the check. The wrapper runs verification before and after the task when enabled.

State/persistence behavior: verification is read-only; task reporting still persists schedule run info through `ReportRun`.

Dependencies/integration: integrates content reader verification, maintenance task reporting, random sampling, and environment configuration.

Risks/test signals: random sampling makes failures probabilistic unless percentage is 100. The verification can add substantial maintenance cost, so it is opt-in.
