## sources/user-network-fs/gcsfuse/perfmetrics/scripts/fio/testdata/partial_metrics.json

Purpose: Fixture for mixed valid and invalid/zero jobs.

APIs and structure: Contains multiple jobs where the first selected job has zero metrics and a later job has populated read metrics. This validates skip-and-continue behavior.

Control flow and state: No code; parser should skip all-zero job metrics but still return later valid records.

Dependencies and risks: Required metric keys must remain present in zeroed jobs to test skip behavior rather than missing-key failure.

Test signals: Expected output is one valid metrics record from the nonzero job.
