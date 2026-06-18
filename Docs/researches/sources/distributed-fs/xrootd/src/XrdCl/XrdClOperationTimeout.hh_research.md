# sources/distributed-fs/xrootd/src/XrdCl/XrdClOperationTimeout.hh

## Purpose

This header defines a lightweight timeout budget object for operation pipelines. It converts an original timeout into remaining seconds and throws when the operation has expired.

## Important APIs, Types, And Functions

`operation_expired` is an exception marker. `Timeout` has default and timeout constructors, copy constructor, assignment operator, and conversion operator `operator time_t() const`.

## Control Flow

Pipeline code stores a `Timeout` and passes it to operation runs. When converted to `time_t`, a zero timeout returns zero, otherwise elapsed wall-clock seconds are subtracted from the original budget. If elapsed time exceeds the budget, `operation_expired` is thrown and pipeline execution maps it to `errOperationExpired`.

## State And Persistence

`Timeout` stores `timeout` and `start` as `time_t`. There is no persistence. Copies preserve the original start time, so the budget travels through the pipeline.

## Dependencies And Integration Points

It uses `<ctime>`, `<cstdint>`, and `<exception>`. `XrdClOperations.hh` catches `operation_expired` in `Operation::Run`.

## Risks

The implementation uses `time(0)`, so system clock jumps can lengthen or shorten budgets. Resolution is one second. `operation_expired` does not override `what()`, which is fine for control flow but less useful for diagnostics.

## Test Signals

Tests should check zero timeout behavior, remaining-time conversion after delays, copy/assignment preserving start time, expiration throwing, boundary behavior when elapsed equals timeout, and pipeline mapping to `errOperationExpired`.
