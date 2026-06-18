<!-- BEGIN_FILE_RESEARCH: sources/object-store/garage/src/util/error.rs -->
# sources/object-store/garage/src/util/error.rs

## Purpose
Shared Garage utility error type and ergonomic conversion helpers for IO, serialization, TOML, HTTP, database, channel, and internal message errors.

## Important APIs, types, and functions
`Error` enum includes variants for DB, IO, RMP encode/decode, JSON, TOML, HTTP, hyper, invalid HTTP headers, and messages. Helpers include `unexpected_rpc_message`, `ErrorContext`, `OkOrMessage`, custom serde serialization/deserialization, and conversions from transaction and channel send errors.

## Control flow
Most functions propagate errors with `?` into this enum. Context helpers wrap lower-level errors in message text. Serialization of `Error` deliberately stores only string form, and deserialization reconstructs a message error.

## State and persistence behavior
Errors are not persistent domain state, but serializing them over RPC loses structured variant detail. This is acceptable for reporting but not for programmatic remote recovery logic.

## Dependencies and integration points
Used throughout Garage utility, table, web, and RPC code. Depends on `thiserror`, serde, HTTP/hyper, rmp-serde, TOML, and Garage DB.

## Risks and test signals
String-only error serialization can hide variant-specific behavior. Tests should exercise context helpers, transaction conversion, and RPC round-trips where callers expect a message-only remote error.
<!-- END_FILE_RESEARCH: sources/object-store/garage/src/util/error.rs -->
