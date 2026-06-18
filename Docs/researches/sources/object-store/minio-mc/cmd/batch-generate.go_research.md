# sources/object-store/minio-mc/cmd/batch-generate.go

## Purpose

`batch-generate.go` implements `mc batch generate`, producing batch job templates or listing supported job types.

## Important APIs, Types, and Functions

`batchGenerateCmd` defines the command. `mainBatchGenerate` calls `GetSupportedBatchJobTypes`, `GenerateBatchJobV2`, or legacy `GenerateBatchJob` depending on input and server capability.

## Control Flow

The handler validates target and job type. For `list`, it asks the server for supported types and falls back to `madmin.SupportedJobTypes` when the API is unavailable, printing JSON or one type per line. For templates, it tries V2 generation first; if unavailable it verifies the job type against static supported types and calls the legacy generator.

## State and Persistence Behavior

The command reads server capabilities/templates and writes stdout only.

## Dependencies and Integration Points

It uses `madmin.GenerateBatchJobOpts`, static `madmin.SupportedJobTypes`, color JSON, and batch group registration.

## Risks and Edge Cases

Server API availability affects output source. Unknown job types are rejected only after V2 reports unavailable. Direct stdout bypasses normal message wrapping.

## Test Signals

Tests should cover supported type list in JSON/plain modes, V2 success, V2 unavailable fallback, unsupported type failure, and API errors.
