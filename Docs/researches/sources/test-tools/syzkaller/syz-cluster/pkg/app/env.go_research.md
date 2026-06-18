# sources/test-tools/syzkaller/syz-cluster/pkg/app/env.go

## Purpose
Dependency injection setup for production and tests.

## Important APIs, Types, and Functions
AppEnvironment, Environment, TestEnvironment, DefaultSpannerURI, DefaultSpanner, DefaultStorage, DefaultClient, DefaultReporterClient.

## Control Flow
Production setup reads env/config and constructs Spanner/GCS/URL dependencies; tests create transient Spanner DB and local blob storage.

## State and Persistence
Holds shared clients/config; durable state lives in Spanner and blob storage.

## Dependencies and Integration Points
Integrates configuration, environment variables, Spanner, blob storage, URL generation, and test harness setup.

## Risks and Edge Cases
Risks include hard-coded paths/service URLs, cached config reload limitations, and operational env var mistakes.

## Test Signals
Covered by config overlay tests and broad app.TestEnvironment integration tests.
