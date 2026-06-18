# sources/object-store/rustfs/crates/madmin/src/utils.rs

Purpose: small utility module currently dedicated to human-readable duration parsing.

Important APIs/types/functions: `parse_duration(s: &str) -> Result<Duration, String>` wraps `humantime::parse_duration` and converts the parser error to a `String`.

Control flow: no custom parsing logic remains despite comments suggesting one. All duration grammar, units, and error wording are delegated to `humantime`.

State and persistence: none.

Dependencies/integration: depends on `std::time::Duration` and the `humantime` crate. `service_commands.rs` uses it to parse trace threshold query parameters.

Risks: accepted syntax is exactly `humantime` syntax, which may be broader than the admin API intends. Returning `String` errors loses structured error information. Comments are stale and could mislead maintainers into thinking the parser is custom.

Test signals: unit test `test_parse_dur` verifies `3s`, `3ms`, `3m`, and `3h` map to expected `Duration` values. Invalid input and compound durations are not covered here.
