# sources/user-network-fs/gcsfuse/tools/integration_tests/util/creds_tests/creds.go

## Purpose

Provides shared credential-test setup for gcsfuse integration suites that need to verify `--key-file` and `GOOGLE_APPLICATION_CREDENTIALS` authentication behavior with controlled service-account permissions.

## Important APIs, control flow, and dependencies

`projectID` reads metadata server project ID, maps cloudtop environments to a whitelisted test project, and logs when the project is not whitelisted. `CreateCredentials` and `CreateCredentialsForSA` fetch a service account key from Secret Manager and write it to a temp JSON file. IAM helpers add and remove storage roles or custom roles on a bucket. `RunTestsForDifferentAuthMethods` creates credentials, grants the requested permission, runs tests with `GOOGLE_APPLICATION_CREDENTIALS`, then with both env var and `--key-file`, then with `--key-file` only. A deprecated wrapper builds a config from setup flags.

## State, persistence, dependencies, and integration points

The utility mutates bucket IAM policy and local process environment, writes a temporary credential file, and depends on metadata, Secret Manager, IAM, storage client, static mounting, and test-suite config. It deliberately sleeps two minutes after IAM changes for propagation before running mounts.

## Risks and test signals

Risks include long IAM propagation delays, fatal exits on secret/IAM failures, leaked credentials or environment variables if execution aborts, and tests running in non-whitelisted projects with only a log warning. Signals are successful mount/test runs under all three credential combinations and deferred role revocation and temp-file cleanup.
