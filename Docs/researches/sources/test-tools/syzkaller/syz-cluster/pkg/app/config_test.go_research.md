# sources/test-tools/syzkaller/syz-cluster/pkg/app/config_test.go

## Purpose
Deployment overlay config validation test.

## Important APIs, Types, and Functions
TestConfigs walks syz-cluster/overlays and loads every global-config.yaml.

## Control Flow
Discovers files from the pkg/app working directory and subtests each config.

## State and Persistence
Reads checked-in config files only.

## Dependencies and Integration Points
Integrates configuration, environment variables, Spanner, blob storage, URL generation, and test harness setup.

## Risks and Edge Cases
Risks include hard-coded paths/service URLs, cached config reload limitations, and operational env var mistakes.

## Test Signals
Covered by config overlay tests and broad app.TestEnvironment integration tests.
