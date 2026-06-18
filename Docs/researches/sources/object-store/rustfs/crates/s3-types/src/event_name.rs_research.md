<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/s3-types/src/event_name.rs -->
# sources/object-store/rustfs/crates/s3-types/src/event_name.rs

## Purpose
Defines RustFS S3 notification event names, parsing/formatting, compound event expansion, bitmask generation, schema version selection, and serde integration.

## Important APIs, types, and functions
- `EventName` enumerates object accessed/created/removed, bucket, replication, restore, transition, lifecycle, scanner, ACL/tagging, intelligent-tiering, compound `All` variants, `Everything`, and internal metrics events.
- `ParseEventNameError` reports invalid strings.
- `EventName::parse`, `try_from_event_str`, `as_str`, `expand`, and `mask` implement string and mask behavior.
- `event_schema_version` returns S3 notification schema version `2.1`, `2.2`, or `2.3`.
- `Display`, `From<&str>`, `Serialize`, and `Deserialize` connect event names to external representations.

## Control flow
Parsing is an explicit string match over supported S3 event strings and aliases. Formatting matches enum variants back to strings, with `Everything` formatting as an empty string for Go compatibility. `expand` maps compound variants to their concrete single-event lists, and `mask` uses sequential discriminants for single events or recursively ORs expanded masks for compound events.

## State and persistence behavior
There is no mutable state. The enum discriminants and mask layout are a persistence-sensitive contract for event filter masks. Serialized strings are part of S3 notification configuration and emitted event payloads.

## Dependencies and integration points
Depends on `std::fmt`, `serde`, and `serde_json` in tests. `rustfs-s3-ops` consumes `EventName` for operation mapping, and notification configuration/delivery code can use masks and schema versions.

## Risks and edge cases
Single-event discriminants must remain sequential through `LAST_SINGLE_TYPE_VALUE` or masks will change. `SINGLE_EVENT_NAMES_IN_ORDER` currently has 32 entries, while later single events are appended through `SINGLE_AWS_AND_EXTENSION_EVENTS_AFTER_COMPAT`; this preserves compatibility but requires care when adding events. `From<&str>` panics on invalid input, so fallible parsing is safer for external config. Internal events have strings but are not accepted by `parse`.

## Test signals
Tests cover serde round trips, invalid deserialization including empty `Everything`, alias parsing, AWS-compatible `ObjectCreatedAll` expansion, schema version mapping, and `try_from_event_str` success/failure.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/s3-types/src/event_name.rs -->
