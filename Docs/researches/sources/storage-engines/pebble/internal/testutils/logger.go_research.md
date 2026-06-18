# sources/storage-engines/pebble/internal/testutils/logger.go

## Purpose
This file adapts `testing.TB` to a logger-like interface for tests.

## Important APIs, Types, and Functions
`Logger` stores `T testing.TB`. `Infof` and `Errorf` forward to `T.Logf`. `Fatalf` marks itself as helper and forwards to `T.Fatalf`.

## Control Flow and State
All methods are direct delegation. The only state is the wrapped test handle.

## Dependencies and Integration
It depends on `testing`. It is useful for code under test that accepts a logger interface while tests want log output attached to the running test.

## Risks and Edge Cases
`Errorf` logs rather than failing the test, so callers expecting error-level logs to fail must use a different adapter. `Logger` assumes `T` is non-nil.

## Test Signals
No direct tests are included. Behavior is simple and normally validated by consumers.
