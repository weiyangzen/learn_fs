# sources/object-store/rustfs/crates/policy/src/serde_datetime.rs

## Purpose

Provides serde helpers for IAM timestamps. Serialization always emits RFC3339, while deserialization accepts RFC3339 and a legacy RustFS human-readable timestamp format.

## Important APIs, Types, and Functions

- `LEGACY_FORMAT` is a `OnceLock<OwnedFormatItem>` for the legacy parser.
- `legacy_format()` lazily parses the legacy `time` format description.
- `parse_rfc3339_or_legacy(s)` tries `Rfc3339` first and falls back to the legacy format.
- `serialize(dt, serializer)` delegates to `time::serde::rfc3339`.
- `deserialize(deserializer)` reads a string and parses it with the compatibility parser.
- `option::serialize` and `option::deserialize` provide the same behavior for `Option<OffsetDateTime>`.

## Control Flow

Deserialization reads borrowed string data from serde, attempts RFC3339 parsing, and on failure attempts the legacy format `YYYY-MM-DD HH:MM:SS.ffffff +00:00:00`. Errors are converted to serde custom errors. Option serialization emits `Some` as an RFC3339 string and `None` as null/none.

## State and Persistence

Only global state is the lazily initialized legacy format descriptor. No persistence or I/O.

## Dependencies and Integration Points

Used by policy data types that need stable timestamp wire formats. Depends on `serde` and `time` formatting/parsing. The comments call out MinIO compatibility.

## Risks and Edge Cases

- Legacy parser expects fractional seconds and an offset with seconds. Legacy timestamps that omit fractional or offset seconds will fail.
- Serialization normalizes all supported inputs to RFC3339, so legacy formatting is read-only compatibility.
- `legacy_format().expect` will panic only if the hard-coded format description is invalid.

## Test Signals

Inline tests verify legacy RustFS timestamp parsing and RFC3339 parsing through a transparent serde wrapper.
