# sources/storage-engines/foundationdb/flow/include/flow/Error.h

## Purpose
`Error.h` defines Flow's compact error object, generated error factory functions/codes, assertion macros, injected-fault tagging, and build feature macros.

## Important APIs, Types, And Functions
Key items are `ErrorCodeTable`, `Error`, `systemErrorCodeToError()`, `transactionRetryableErrors`, generated `ERROR()` functions from `error_definitions.h`, `AttributeNotFoundError`, `actor_cancelled()`, `internal_error_impl()`, `ASSERT*` macros, `ABORT_ON_ERROR`, `ENABLED`/`DISABLED`, and clean-build guards.

## Control Flow
Error factories construct an `Error` by numeric code. `Error::init()` populates the code table. Assertions call `internal_error_impl()` with file/line and traced values, unless the line is disabled. `ABORT_ON_ERROR` catches Flow or unknown exceptions and terminates through `criticalError`.

## State And Persistence Behavior
`Error` stores a 16-bit code and 16-bit flags and serializes only the code. The global error table and retryable set provide lookup metadata. Injected-fault status is a flag on the transient error object.

## Dependencies And Integration Points
It depends on actor context, platform exit handling, knobs, file identifiers, serialization traits, traceable formatting, Boost preprocessor macros, and generated error definitions. Nearly every Flow actor and interface uses this contract.

## Risks And Edge Cases
Only the code serializes, so flags such as injected fault do not persist. Throwing assertions in destructors is unsafe, hence `ASSERT_ABORT`. `actor_cancelled` aliases `operation_cancelled`, so code comparisons must use the modern code. Feature macros intentionally fail if passed unexpected text.

## Test Signals
Signals include error table initialization, name/description lookup, serialization round trips, unvalidated code conversion, injected-fault tagging, assertion diagnostics, retryable set membership, and clean-build macro behavior.
