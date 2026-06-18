# sources/object-store/minio-mc/cmd/batch-start.go

## Purpose

`batch-start.go` implements `mc batch start`, submitting a batch job definition file to the server.

## Important APIs, Types, and Functions

`batchStartCmd` defines the command. `batchStartMessage` wraps `madmin.BatchJobResult`. `mainBatchStart` reads the job file and calls `StartBatchJob`.

## Control Flow

The handler validates target and job-file path, creates an admin client, reads the entire file into memory, creates a cancellable context, sends the file content as a string to `StartBatchJob`, and prints the result.

## State and Persistence Behavior

The server persists or starts the batch job. Locally, the command reads a YAML/JSON definition file but writes no files.

## Dependencies and Integration Points

It uses file IO, `madmin.StartBatchJob`, shared output helpers, and batch command registration.

## Risks and Edge Cases

The whole job file is loaded into memory. File content validation is server-side. Success text includes `Started` with `%s`, relying on its string formatting.

## Test Signals

Tests should cover missing file, invalid arity, file content propagation, API errors, and result message rendering.
