# sources/user-network-fs/gcsfuse/tools/integration_tests/readonly/readonly_test.go

## Purpose

`readonly_test.go` is the harness and fixture setup for read-only integration tests. It seeds a known object hierarchy, defines shared constants, configures read-only mount variants, and runs the package under static, persistent, and viewer-credential modes.

## Important APIs, Types, and Functions

Constants define the fixture tree, expected object counts, file contents, missing names, and rename targets. `createTestDataForReadOnlyTests` writes three objects to the target bucket using the storage client. `checkErrorForObjectNotExist` validates not-found errors by substring. `TestMain` handles config, environment, storage client, fixture creation, mounted-directory mode, path rewriting, flag-set generation, and test execution.

## Control Flow

`TestMain` parses flags, loads or synthesizes `ReadOnly` config, sets up storage client and bucket environment, writes fixture objects, optionally delegates to mounted-directory mode, prepares test directories and rewritten paths, builds flag sets, then runs tests first with static mounting, then persistent mounting, then with `creds_tests.RunTestsForDifferentAuthMethods` using objectViewer permissions.

## State and Persistence Behavior

Fixture objects persist in GCS for the package run. The harness may use read-only flags, restrictive file/dir modes, gRPC, and file cache. It mutates global `storageClient` and `ctx`. It does not explicitly clean the fixture prefix in this file, so cleanup is delegated to broader setup or test environment.

## Dependencies and Integration Points

It depends on Cloud Storage, integration `client`, credential test helpers, static/persistent mounting helpers, setup/test-suite helpers, and sibling test files. It integrates with IAM behavior by re-running tests under viewer credentials.

## Risks and Edge Cases

The suite changes bucket permissions for credential variants, so it is listed as non-parallel in the e2e runner. Fixture setup writes directly to GCS before read-only mounting; failures there invalidate all tests. Error validators rely on string matching. Cleanup gaps can leave seeded objects if broader cleanup fails.

## Test Signals

A full pass demonstrates that read/list/stat operations work while create/write/append/copy/delete/rename fail across read-only flag styles, persistent mount, file cache, gRPC, and viewer credentials.
