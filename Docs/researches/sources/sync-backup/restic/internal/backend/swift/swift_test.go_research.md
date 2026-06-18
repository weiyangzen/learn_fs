<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/swift/swift_test.go -->
# sources/sync-backup/restic/internal/backend/swift/swift_test.go

## Purpose
Runs the generic backend suite and benchmarks against a configured Swift endpoint.

## Important APIs, Types, And Functions
newSwiftTestSuite, TestBackendSwift, and BenchmarkBackendSwift are key.

## Control Flow
Tests read environment/config values, choose unique prefixes, construct a Swift factory, and run shared tests/benchmarks when required variables are available.

## State And Persistence Behavior
Uses remote Swift state and environment-provided credentials.

## Dependencies And Integration Points
Depends on backend/test Suite, swift.NewFactory, options, and internal/test skip helpers.

## Risks And Edge Cases
Skipped without environment; failures can reflect remote Swift service behavior.

## Test Signals
Provides integration coverage for Swift backend contract compliance.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/swift/swift_test.go -->
