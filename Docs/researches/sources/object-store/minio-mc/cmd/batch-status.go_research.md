# sources/object-store/minio-mc/cmd/batch-status.go

## Purpose

`batch-status.go` implements `mc batch status`, showing real-time or last-known metrics for a batch job.

## Important APIs, Types, and Functions

`batchStatusCmd` defines the command. `batchJobStatusMessage` wraps `madmin.JobMetric`. `mainBatchStatus` orchestrates live metrics or completed-job lookup. `batchJobMetricsUI` is a Bubble Tea model that renders job metrics for replication, expiration, and catalog jobs.

## Control Flow

The handler validates target and job ID, creates an admin client, calls `DescribeBatchJob` to decide whether the job is active, and creates a metrics UI. If the job no longer exists as active, it calls `BatchJobStatus` once. Otherwise it streams `client.Metrics` with `MetricsBatchJobs`, `ByJobID`, and one-second interval. JSON mode prints each metric and cancels on complete/failed; non-JSON mode sends metrics to the Bubble Tea UI.

## State and Persistence Behavior

Remote metrics are read only. Local runtime state is the UI model's latest metric, spinner, and quitting flag.

## Dependencies and Integration Points

It depends on `madmin` batch metrics APIs, Bubble Tea, Bubbles spinner, humanize formatting, tablewriter, context cancellation, and global JSON mode.

## Risks and Edge Cases

The UI assumes known job type metric substructures. Catalog scan speed divides by elapsed seconds, which can be zero for early metrics. JSON mode waits on context cancellation and depends on streaming callback cancellation behavior.

## Test Signals

Tests should cover active versus historical job branch, JSON status transitions, context cancellation, UI quitting on complete/failed, each job type rendering, and missing job metrics.
