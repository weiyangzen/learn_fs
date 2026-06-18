<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/badger/logger_test.go -->
# sources/storage-engines/badger/logger_test.go

## Purpose
This file tests the `Options` logging delegation surface using a mock logger.

## Important APIs, Types, And Functions
`mockLogger` implements `Logger` by writing the formatted severity-prefixed message into `output`. `TestDbLog` calls `Options.Errorf`, `Infof`, and `Warningf`. `TestNoDbLog` repeats the same calls after assigning a mock logger to an otherwise empty `Options`.

## Control Flow
Each test constructs an `Options` value with a mock logger, invokes logging helpers, and checks the final string in the mock after each call. The tests are simple synchronous delegation checks.

## State And Persistence Behavior
The only state is `mockLogger.output`. There is no filesystem or DB state.

## Dependencies And Integration Points
The test depends on `fmt.Sprintf`, `testing`, and `testify/require`. It validates the logging facade used by the rest of Badger.

## Risks And Edge Cases
The "no DB log" name is misleading because the test still assigns `opt.Logger = l`; it does not cover nil-logger suppression. Debug logging and default severity filtering are also not covered.

## Test Signals
The signal is exact prefix-preserving formatted output for error, info, and warning methods.
<!-- END_FILE_RESEARCH: sources/storage-engines/badger/logger_test.go -->
