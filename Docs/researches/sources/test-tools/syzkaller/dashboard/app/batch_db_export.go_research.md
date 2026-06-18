# sources/test-tools/syzkaller/dashboard/app/batch_db_export.go

Purpose: weekly cron entry point for launching Cloud Batch jobs that export dashboard reproducer data for namespaces configured with an archive path.

Important APIs and functions: `handleBatchDBExport` iterates all namespace configs, skips namespaces without `ReproExportPath`, constructs a Batch service account with userinfo email scope, and calls `createScriptJob` with the `db-export` prefix and a six-hour timeout. `exportDBScript` returns the job shell script: clone syzkaller, acquire a gcloud access token, run `tools/syz-db-export` for the source namespace with parallelism `-j 10`, tar the export directory, and copy the archive to the configured storage path.

Control flow: `/cron/batch_db_export` is scheduled in `cron.yaml` every Saturday. The handler logs job creation failures per namespace and continues with the remaining namespaces.

State and persistence behavior: the app itself only reads config and schedules Batch jobs. The external job reads dashboard data through the exporter tool and writes a compressed archive to cloud storage. No datastore writes occur in this handler.

Dependencies and integration points: uses `CoverageConfig`-independent namespace field `ReproExportPath`, Cloud Batch service accounts, `createScriptJob` from `batch_main.go`, `gcloud`, and the syzkaller repository tooling. The hardcoded project for exports is `syzkaller`.

Risks: shell script construction trusts namespace and archive path from config. Export freshness and idempotency depend on external storage object semantics and the exporter tool. The service account only requests userinfo email scope here, so any future exporter authentication needs must be reflected in scopes.

Test signals: no direct test in this subset. Operational coverage comes from cron wiring and shared Batch creation code.
