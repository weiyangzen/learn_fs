<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/obs/src/logging.rs -->
# sources/object-store/rustfs/crates/obs/src/logging.rs

## Purpose
Defines log redaction policy and helper functions to prevent secrets and sensitive principal identifiers from being emitted in observability logs.

## Important APIs, Types, and Functions
`REDACTED_LOG_VALUE` is the replacement string. `LOGGING_REDACTION_RULES` lists sensitive fields such as access key, authorization, client secret, secret key, session token, and token. `validate_logging_redaction_rules` delegates to security-governance validation. `is_sensitive_log_field` checks fields case-insensitively. `redacted_log_value` preserves empty strings and redacts non-empty values; `redacted_optional_log_value` maps optional values. `MaskedAccessKey` is re-exported from `rustfs_utils`.

## Control Flow
Redaction checks trim and compare field names against the rule list. Helper functions are pure and do not mutate state.

## State and Persistence
No runtime state. The policy is a static slice of `RedactionRule` values.

## Dependencies and Integration
Integrates with `rustfs_security_governance` for rule validation and `rustfs_utils` for access-key masking. Tests inspect source files across the workspace to enforce logging governance patterns.

## Risks
Static field-name matching can miss nested, renamed, or semantically secret fields not in the rule list. The generic `token` rule may redact benign fields named token, but that is a deliberate conservative choice.

## Test Signals
Tests validate policy, case-insensitive detection, empty-value preservation, access key masking, absence of old unmasked logging patterns in auth/protocol/startup/telemetry/audit/notify code, and allowed low-level stderr exceptions.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/obs/src/logging.rs -->
