# sources/storage-engines/tikv/components/log_wrappers/src/lib.rs

## Purpose
`log_wrappers` provides `slog::Value` adapters and redaction-aware byte formatting for keys and values. It lets code log display/debug-only types and user data without requiring third-party types to implement `slog::Value`.

## Important APIs, Types, and Functions
- `DisplayValue<T>` and `DebugValue<T>` serialize via `Display` and `Debug`.
- `RedactOption` represents user-configurable redaction: `Off`, `On`, or `Marker`; it implements `Display`, `FromStr`, `TryFrom<ConfigValue>`, `From<RedactOption> for ConfigValue`, and serde serialization/deserialization.
- `set_redact_info_log` stores a process-global `RedactLevel` and also updates protobuf's redaction level.
- `Value<'a>` wraps bytes for key/value logging. As `slog::Value`, `Display`, and `Debug`, it prints uppercase hex, `"?"`, or marker-wrapped uppercase hex depending on redaction state.

## Control Flow
Redaction parsing accepts booleans and selected case variants. Serialization emits booleans for on/off and string `"marker"` for marker mode. `Value` formatting reads the atomic redaction level at formatting time, so a global config update affects subsequent logs immediately.

## State and Persistence Behavior
`REDACT_INFO_LOG` is static process-global state. It is relaxed-atomic because formatting only needs eventual consistency. No data is persisted, but logs emitted before and after changes may use different redaction levels.

## Dependencies and Integration Points
The file integrates with `online_config::ConfigValue`, protobuf atomic redaction flags, serde/TOML config parsing, `slog`, and the local hex re-export. `keys` and many storage components use `Value::key` in error/log messages.

## Risks
Redaction mode is global; tests and runtime config changes must restore desired state to avoid cross-test or cross-module surprises. Accepted strings are asymmetric (`MARKER` accepted, `Marker` rejected), so UI/config layers must match parser behavior. With `Off`, raw user data is hex-encoded but still present in logs.

## Test Signals
Tests validate debug wrapper output with a deterministic logger, uppercase key logging, redaction option parsing/serde conversion, config-value conversion, and output for off/on/marker modes.
