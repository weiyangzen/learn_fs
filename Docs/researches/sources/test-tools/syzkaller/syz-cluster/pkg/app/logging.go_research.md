# sources/test-tools/syzkaller/syz-cluster/pkg/app/logging.go

## Purpose
Minimal application logging wrappers.

## Important APIs, Types, and Functions
Errorf and Fatalf.

## Control Flow
Delegates to standard log.Printf/log.Fatalf.

## State and Persistence
No durable state.

## Dependencies and Integration Points
Integrates configuration, environment variables, Spanner, blob storage, URL generation, and test harness setup.

## Risks and Edge Cases
Risks include hard-coded paths/service URLs, cached config reload limitations, and operational env var mistakes.

## Test Signals
Covered by config overlay tests and broad app.TestEnvironment integration tests.
