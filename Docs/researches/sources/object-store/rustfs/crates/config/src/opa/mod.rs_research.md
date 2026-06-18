<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/config/src/opa/mod.rs -->
# sources/object-store/rustfs/crates/config/src/opa/mod.rs

## Purpose
Defines OPA/policy plugin environment keys and subsystem name.

## Important APIs, types, and functions
`ENV_POLICY_PLUGIN_OPA_URL` maps to `RUSTFS_POLICY_PLUGIN_URL`, `ENV_POLICY_PLUGIN_AUTH_TOKEN` maps to `RUSTFS_POLICY_PLUGIN_AUTH_TOKEN`, `ENV_POLICY_PLUGIN_KEYS` lists both, and `POLICY_PLUGIN_SUB_SYS` is `policy_plugin`.

## Control flow
No local flow; policy plugin setup reads the URL/token from environment/config.

## State and persistence behavior
The file owns no mutable runtime state and performs no persistence. Its constants become persisted or operator-visible only when other crates serialize configuration, read environment variables, or write queue/config files using these names.

## Dependencies and integration points
Integrates with external OPA or policy plugin authorization checks.

## Risks and edge cases
The auth token is sensitive and must not be logged. A configured external policy URL can become an availability dependency for authorization if downstream code fails closed.

## Test signals
Best test signals are compile-time users continuing to build, startup/config parsing tests that assert the environment key names and defaults, and subsystem tests that verify changed defaults alter runtime behavior only where intended. Policy integration should cover token redaction, URL validation, and authorization behavior when the plugin is unavailable.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/config/src/opa/mod.rs -->
