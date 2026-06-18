# sources/object-store/rustfs/crates/kms/src/time_serde.rs

## Purpose
Provides serde adapters for `jiff::Zoned` timestamps with backward compatibility for legacy RFC3339 timestamp strings.

## Important APIs, Types, And Functions
`zoned::serialize` and `zoned::deserialize` handle required `Zoned` fields. `option_zoned::serialize` and `option_zoned::deserialize` handle `Option<Zoned>`. `parse_zoned_compat` first parses full `Zoned` format and falls back to parsing a `Timestamp` converted to UTC.

## Control Flow
Deserialization reads a string, attempts current `Zoned` parsing, then attempts legacy `Timestamp` parsing. Optional deserialization maps through the same parser and transposes the result.

## State And Persistence
No runtime state. It defines timestamp persistence compatibility for KMS envelopes and any structs using these adapters.

## Dependencies And Integration
Uses `jiff::{Timestamp, Zoned, TimeZone}` and serde traits. `dek.rs` uses `zoned` for `DataKeyEnvelope.created_at`; other KMS types may use it as needed.

## Risks And Edge Cases
Legacy RFC3339 values lose original timezone naming and are normalized to UTC. Parse failures include the legacy value in the error string, so callers should avoid feeding sensitive strings as timestamps.

## Test Signals
Tests confirm current timezone-annotated strings and legacy RFC3339 strings parse and result in UTC timezone metadata.
