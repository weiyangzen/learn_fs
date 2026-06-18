# sources/user-network-fs/gcsfuse/tools/integration_tests/readonly_creds/readonly_creds_test.go

## Purpose

This harness runs readonly-credential tests under an objectViewer credential context, validating failed write/create behavior when the mount is not explicitly read-only but credentials prevent writes.

## Important APIs, Types, and Functions

Constants define the test directory, filename, content, and permission-denied substring. `env` stores storage client, context, config, and bucket type. `TestMain` handles config, environment, storage client lifecycle, GKE skip behavior, initial test directory creation, path rewriting, flag-set generation, credential-mode execution, and cleanup.

## Control Flow

`TestMain` parses flags, loads or synthesizes `ReadonlyCreds` config with implicit-dir variants, initializes environment and storage client, skips mounted-directory/GKE mode, creates the test directory before dropping privileges, prepares mount directories and flags, then calls `creds_tests.RunTestsForDifferentAuthMethods` with role `objectViewer`. It cleans the test prefix from GCS afterward.

## State and Persistence Behavior

The harness creates the GCS test directory while it still has full credentials, then runs tests under restricted credentials. It mutates package global `testEnv`, `mountDir`, and `rootDir`. Cleanup uses the original storage client after credential test execution.

## Dependencies and Integration Points

It depends on Cloud Storage, integration `client`, `creds_tests`, setup/test-suite helpers, and sibling suite tests. It is listed as non-parallel in the e2e runner because credential manipulation can affect shared bucket permissions.

## Risks and Edge Cases

Mounted-directory mode is skipped because the credential switching assumptions do not apply. Permission-denied behavior varies by bucket type and write path. Cleanup must run with sufficient credentials or failed test artifacts can remain.

## Test Signals

Harness success means the readonly-credential suite ran under objectViewer for compatible bucket types and cleaned its test prefix. Failures usually indicate IAM setup, credential generation, or permission semantics regressions.
