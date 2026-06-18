<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/config/src/constants/env.rs -->
# sources/object-store/rustfs/crates/config/src/constants/env.rs

## Purpose
Defines shared configuration vocabulary and a permissive `EnableState` parser used by RustFS config/environment surfaces.

## Important APIs, types, and functions
Core constants include `ENV_PREFIX`, delimiters, default event/audit directories, global audit/notify switches, ILM process-time keys, `ENABLE_KEY`, and `COMMENT_KEY`. `EnableState` has variants for true/false, yes/no, on/off, enabled/disabled, ok/not_ok, success/failure, active/inactive, and 1/0. It implements `Display`, `FromStr`, `as_str`, `is_enabled`, and `is_disabled`.

## Control flow
`FromStr` trims input and performs case-insensitive matching for word values while handling `1` and `0` exactly. `is_enabled` and `is_disabled` classify every variant, with `Empty` treated as disabled.

## State and persistence behavior
The file owns no mutable runtime state and performs no persistence. Its constants become persisted or operator-visible only when other crates serialize configuration, read environment variables, or write queue/config files using these names.

## Dependencies and integration points
This module is re-exported by `config/src/lib.rs` under the `constants` feature and is consumed by notify/audit/server config code that needs uniform enable and comment keys.

## Risks and edge cases
The parser returns `Err(())` for unknown values, so callers need clear error handling. Treating empty as disabled is conservative but can surprise code that wants tri-state semantics. Adding variants requires keeping `as_str`, parsing, and classification in sync.

## Test signals
Unit tests pin all conversions, defaults, enabled/disabled classification, and audit/notify env names. Additional integration tests should ensure callers reject invalid enable strings consistently.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/config/src/constants/env.rs -->
