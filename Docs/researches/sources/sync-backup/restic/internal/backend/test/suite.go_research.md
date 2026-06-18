<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/test/suite.go -->
# sources/sync-backup/restic/internal/backend/test/suite.go

## Purpose
Implements the generic backend contract test runner used by concrete backend tests.

## Important APIs, Types, And Functions
Suite, RunTests, testFuncs, benchmarkFuncs, RunBenchmarks, createOrError, create, open, cleanup, and close are central.

## Control Flow
RunTests obtains config, verifies create/close, reflects Test* methods, runs subtests, and deletes test data if cleanup is enabled. RunBenchmarks reflects Benchmark* methods. Helpers create/open backends through a location.Factory and wrap error handling/cleanup.

## State And Persistence Behavior
State includes Suite.Config and callbacks for config, factory, cleanup policy, delayed removal, and error handling. Repository state is created/deleted through the backend under test.

## Dependencies And Integration Points
Depends on reflection, testing, context, backend/location, internal/errors/test.

## Risks And Edge Cases
Reflection-based discovery means method signatures and names are part of the contract. Cleanup must be robust for remote backends and skipped cleanup mode.

## Test Signals
Exercised by all backend-specific tests that call RunTests or RunBenchmarks.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/test/suite.go -->
