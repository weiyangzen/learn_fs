# sources/test-tools/syzkaller/dashboard/app/batch_coverage.go

Purpose: cron handler for launching Google Cloud Batch jobs that merge raw syzbot coverage data into aggregated coverage periods, plus a cleanup handler for garbage rows in the coverage database.

Important APIs and functions: `handleBatchCoverage` parses `quarters`, `months`, `days`, and `steps` request parameters, selects configured namespaces, finds each namespace's main repo/branch, computes available raw coverage partitions with `nsDataAvailable`, compares them with merged coverage from `coveragedb.NsDataMerged`, and launches bounded merge jobs via `createScriptJob`. `batchCoverageScript` builds the shell script run by Batch, including syzkaller checkout, `syz-env`, optional init scripts, and repeated `tools/syz-bq.sh` invocations. `nsDataAvailable` queries BigQuery partition metadata for per-day raw coverage. `handleBatchCoverageClean` calls `coveragedb.DeleteGarbage` and writes a plain text result.

Control flow: cron URLs in `cron.yaml` run quarter jobs weekly and day/month jobs daily. For each namespace with `Coverage` config, the handler builds a list of periods to merge using day/month/quarter period ops, truncates to the newest `steps`, and starts one Batch job per namespace. Missing coverage config, missing main repo/branch, BigQuery errors, Spanner errors, and job creation failures are logged and do not stop other namespaces.

State and persistence behavior: this file does not mutate datastore directly. It reads BigQuery metadata, reads merged coverage state through the global Spanner client, creates external Batch jobs, and relies on those jobs to write merged coverage back to the coverage DB. The cleanup path mutates the coverage DB by deleting garbage rows.

Dependencies and integration points: integrates with `CoverageConfig`, `mainRepoBranch`, `coveragedb` period math, BigQuery, Cloud Batch service accounts/scopes, dashboard client credentials, and `batch_main.go`'s shared job creation helper.

Risks: request parameter parsing treats missing or malformed `steps` as a logged error and silent return; cron URLs must always include valid steps. `nsDataAvailable` interpolates namespace into a BigQuery `LIKE` pattern, relying on validated namespace config. Script generation concatenates shell fragments from config and parameters; these config values are trusted but operationally sensitive. Batch jobs are fire-and-forget, so duplicate cron runs can schedule overlapping work unless downstream coverage merge code is idempotent.

Test signals: no direct test file in this subset exercises batch coverage. Coverage behavior is indirectly tested by `coverage_test.go` for rendering/queries, and cron scheduling is represented in `cron.yaml`.
