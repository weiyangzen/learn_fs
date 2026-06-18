# sources/object-store/minio-mc/cmd/batch-cancel.go

## Purpose

`batch-cancel.go` implements `mc batch cancel`, canceling an ongoing batch job by ID.

## Important APIs, Types, and Functions

`batchCancelCmd` defines the command and an unused-looking `--id` flag while usage expects positional job ID. `batchCancelMessage` renders success. `mainBatchCancel` calls `CancelBatchJob`.

## Control Flow

The handler validates target and job ID, creates an admin client, creates a cancellable context, calls `adminClient.CancelBatchJob`, and prints a success message.

## State and Persistence Behavior

The server changes batch job state to canceled. The client writes no local state.

## Dependencies and Integration Points

It uses `madmin` batch job APIs, `newAdminClient`, shared message/output helpers, and the batch command group.

## Risks and Edge Cases

The declared `--id` flag is not used by the handler, which can confuse callers. Cancellation outcome and idempotence are server-defined.

## Test Signals

Tests should cover arity, positional job ID propagation, unused flag behavior, API errors, and JSON/text message output.
