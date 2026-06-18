# sources/test-tools/syzkaller/dashboard/app/batch_main.go

Purpose: shared Batch infrastructure for dashboard cron jobs that need to run long external scripts outside App Engine request limits.

Important APIs and functions: `initBatchProcessors` registers `/cron/batch_coverage`, `/cron/batch_db_export`, and `/cron/batch_coverage_clean`. `createScriptJob` creates a Google Cloud Batch job with a generated UUID suffix, one task group, one script runnable, fixed compute resources, timeout, service account, standard `e2-standard-8` VM allocation, Ops Agent installation, and Cloud Logging output.

Control flow: callers pass project ID, job-name prefix, script text, max runtime in seconds, and a service account. The function opens a Batch client, builds protobuf request structs, calls `CreateJob`, logs the created job, and returns detailed errors on client construction or job creation failure.

State and persistence behavior: no dashboard datastore state is touched. Persistent effects are external Cloud Batch jobs and their logs. Job IDs are unique by UUID to avoid name collision.

Dependencies and integration points: used by `batch_coverage.go` and `batch_db_export.go`; initialized from `installConfig` through `initBatchProcessors`. Depends on `cloud.google.com/go/batch/apiv1`, `batchpb`, `uuid`, App Engine logging, and duration protobufs.

Risks: compute shape is hardcoded for coverage workload assumptions and is shared with DB export. Standard provisioning avoids spot preemption but increases cost. Scripts are text blobs, so caller-side escaping and trusted inputs are important. There is no deduplication or checking for already-running jobs.

Test signals: no direct tests in this subset; behavior is mostly operational and external-service dependent.
