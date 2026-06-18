# sources/object-store/minio-mc/cmd/batch-describe.go

## Purpose

`batch-describe.go` implements `mc batch describe`, printing the stored job definition for a batch job.

## Important APIs, Types, and Functions

`batchDescribeCmd` declares the command. `checkBatchDescribeSyntax` enforces target and job ID. `mainBatchDescribe` calls `DescribeBatchJob`.

## Control Flow

The handler validates args, creates an admin client, calls `DescribeBatchJob` with a cancellable context, and prints the returned job definition directly with `fmt.Println`.

## State and Persistence Behavior

The command reads remote batch job definition state only and writes stdout.

## Dependencies and Integration Points

It integrates with `madmin.AdminClient.DescribeBatchJob`, batch command registration, and common error handling.

## Risks and Edge Cases

Direct printing bypasses `printMsg`, so JSON mode does not wrap or transform output. Output format depends on server-returned string content.

## Test Signals

Tests should cover exact arity, API call arguments, direct stdout behavior, and error handling.
