# sources/user-network-fs/gcsfuse/tools/integration_tests/requester_pays_bucket/setup_test.go

## Purpose

This harness configures and runs requester-pays bucket tests. It enables requester-pays on the bucket when needed, injects billing project and service-account key flags, and runs tests under static and only-dir mounting.

## Important APIs, Types, and Functions

Constants define test prefixes, service account name, Secret Manager credential name, and target billing project. `env` stores test directory, storage client, context, and bucket name. `TestMain` is the full setup/teardown orchestrator.

## Control Flow

`TestMain` rejects zonal buckets, loads or synthesizes config, replaces `${BILLING_PROJECT}` and `${KEY_FILE}` placeholders in non-GKE mode, creates a temporary service-account key with `creds_tests.CreateCredentialsForSA`, extracts the billing project from flags, sets it globally, creates the storage client, enables requester-pays if not already enabled, handles mounted-directory mode, builds flag sets, prepares the bucket test directory, runs static mounting, then only-dir mounting, saves logs on failure, cleans the test prefix, and disables requester-pays if this run enabled it.

## State and Persistence Behavior

The harness mutates bucket-level requester-pays configuration and may create a temporary key file on local disk. It records whether requester-pays was already enabled to avoid disabling a pre-existing state. It creates/removes GCS test prefixes. Billing project is stored in setup global state for clients and helpers.

## Dependencies and Integration Points

It depends on Cloud Storage, credential helpers, static/only-dir mounting, setup/test-suite helpers, and client helpers for enabling/disabling requester-pays. It integrates with e2e scripts that run requester-pays scenarios separately.

## Risks and Edge Cases

Requester-pays is a bucket-level setting, so failed cleanup can leave billing behavior changed. The harness requires specific service account, secret, IAM roles, and billing project. Placeholder replacement and billing-project extraction are string-based. Zonal buckets are unsupported and fail fast.

## Test Signals

Success means the bucket was mounted with billing credentials and operations passed in static and only-dir modes. Failures usually point to IAM, Secret Manager, billing project, requester-pays enablement, or mount flag substitution issues.
