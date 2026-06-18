<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/credentials/src/constants.rs -->
# sources/object-store/rustfs/crates/credentials/src/constants.rs

## Purpose
Defines default root credentials, RPC secret env name, IAM policy type strings, and service-account policy claim name.

## Important APIs, types, and functions
`DEFAULT_ACCESS_KEY` and `DEFAULT_SECRET_KEY` are both `rustfsadmin`. `ENV_RPC_SECRET` is `RUSTFS_RPC_SECRET`. IAM constants include embedded/inherited policy type strings and `IAM_POLICY_CLAIM_NAME_SA` as `sa-policy`.

## Control flow
No runtime flow except tests asserting default values and minimum lengths.

## State and persistence behavior
The file owns no mutable runtime state and performs no persistence. Its constants become persisted or operator-visible only when other crates serialize configuration, read environment variables, or write queue/config files using these names.

## Dependencies and integration points
Consumed by credential initialization, RPC token derivation, IAM/service-account classification, and operator environment parsing.

## Risks and edge cases
Default access and secret keys are intentionally insecure for production and must be changed. `ENV_RPC_SECRET` fallback behavior is implemented in `credentials.rs`, so docs/comments must stay aligned.

## Test signals
Unit tests pin defaults and length checks. Integration should warn or reject defaults in production paths where applicable.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/credentials/src/constants.rs -->
