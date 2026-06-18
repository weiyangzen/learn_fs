# sources/object-store/minio-mc/cmd/batch-list.go

## Purpose

`batch-list.go` implements `mc batch list` / `ls`, listing batch jobs and deriving a current status for each job.

## Important APIs, Types, and Functions

`batchListFlags` defines `--type`. `batchListMessage` stores `[]madmin.BatchJobResult` plus an admin client used during rendering. Its `String` and `JSON` methods call `BatchJobStatus` per job to derive completed, in-progress, failed, or unknown status. `mainBatchList` calls `ListBatchJobs`.

## Control Flow

The handler validates one target, creates an admin client, lists jobs filtered by job type, and prints a `batchListMessage`. Rendering builds a table or JSON array and performs additional status lookups for each job.

## State and Persistence Behavior

The command reads remote batch job state only. Runtime output rendering performs network calls via the embedded admin client.

## Dependencies and Integration Points

It integrates `madmin.ListBatchJobs`, `BatchJobStatus`, tablewriter output, humanized times, global JSON mode, and batch command registration.

## Risks and Edge Cases

Rendering has side effects: `String` and `JSON` can make network calls and print errors with `println`. It uses `context.Background()` rather than command context for status lookups. Job ordering depends on server response.

## Test Signals

Tests should cover empty jobs, type filter propagation, status derivation, status lookup failure, JSON shape, and avoiding network calls during pure serialization if refactored.
