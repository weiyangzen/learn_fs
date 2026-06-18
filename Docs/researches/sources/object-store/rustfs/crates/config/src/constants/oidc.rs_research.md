<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/config/src/constants/oidc.rs -->
# sources/object-store/rustfs/crates/config/src/constants/oidc.rs

## Purpose
Defines OpenID Connect admin KVS keys, environment names, valid-key arrays, defaults, and subsystem name.

## Important APIs, types, and functions
KVS keys include config URL, client id/secret, scopes, other audiences, redirect URI/static-dynamic controls, claim name/prefix, role policy, display name, groups/roles/email/username claims, and hide-from-UI. Env arrays `ENV_IDENTITY_OPENID_KEYS` and config-key array `IDENTITY_OPENID_KEYS` include enable/comment boundaries. Defaults set scopes to `openid,profile,email`, group claim to `groups`, roles claim empty, email `email`, username `preferred_username`, and subsystem `identity_openid`.

## Control flow
No executable flow; parser code elsewhere maps environment/config entries by these arrays.

## State and persistence behavior
The file owns no mutable runtime state and performs no persistence. Its constants become persisted or operator-visible only when other crates serialize configuration, read environment variables, or write queue/config files using these names.

## Dependencies and integration points
Integrates with identity provider configuration, console login, STS/IAM claim extraction, and admin config validation.

## Risks and edge cases
Client secret and auth-related keys are sensitive; downstream debug/UI code must respect hidden or redaction policy. The empty default roles claim preserves legacy behavior but may surprise deployments expecting role merging. Array lengths must stay consistent with element count.

## Test signals
Best test signals are compile-time users continuing to build, startup/config parsing tests that assert the environment key names and defaults, and subsystem tests that verify changed defaults alter runtime behavior only where intended. OIDC integration tests should validate default claims, hidden UI behavior, secret redaction, env override mapping, and config-key validation.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/config/src/constants/oidc.rs -->
