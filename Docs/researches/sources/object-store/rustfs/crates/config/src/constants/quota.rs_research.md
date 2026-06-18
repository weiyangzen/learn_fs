<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/config/src/constants/quota.rs -->
# sources/object-store/rustfs/crates/config/src/constants/quota.rs

## Purpose
Defines quota configuration filename, supported quota type, admin API route, S3-style error codes, and user-facing error messages.

## Important APIs, types, and functions
Key constants are `QUOTA_CONFIG_FILE`, `QUOTA_TYPE_HARD`, quota exceeded/invalid/not-found/internal error codes, `QUOTA_API_PATH`, and messages for unsupported quota types and missing bucket metadata system.

## Control flow
No runtime flow; quota handlers use these constants while parsing/administering bucket quotas and returning errors.

## State and persistence behavior
The file owns no mutable runtime state and performs no persistence. Its constants become persisted or operator-visible only when other crates serialize configuration, read environment variables, or write queue/config files using these names.

## Dependencies and integration points
Integrates with bucket metadata persistence (`quota.json`), admin API routing, and S3-compatible error response generation.

## Risks and edge cases
Only HARD quota is supported; adding soft quotas requires changing validation and user messages. The API path embeds `{bucket}` and must match router syntax. Error code changes can break clients.

## Test signals
Best test signals are compile-time users continuing to build, startup/config parsing tests that assert the environment key names and defaults, and subsystem tests that verify changed defaults alter runtime behavior only where intended. Quota integration tests should cover config file read/write, hard quota enforcement, unsupported type rejection, missing bucket handling, and API route matching.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/config/src/constants/quota.rs -->
