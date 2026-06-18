# sources/object-store/rustfs/crates/audit/tests/config_parsing_test.rs

## Purpose
This test file documents audit target configuration conventions independently from concrete target implementations. It checks supported field names, section naming, environment variable shape, merge precedence, duration parsing expectations, URL syntax validation, and MQTT QoS parsing.

## Important APIs, Types, and Functions
Tests use `rustfs_config::server_config::KVS` and a local `parse_duration_test` helper. Covered webhook fields include `enable`, `endpoint`, TLS/client auth fields, batch/queue settings, retry settings, and timeout. MQTT fields cover broker/topic/auth, QoS, keepalive/reconnect intervals, queue settings, TLS options, and websocket path allowlist.

## Control Flow
The tests are pure unit checks. Config merge is simulated by extending default KVS with instance KVS, then environment KVS, establishing precedence as default < instance < environment. Duration parsing checks suffixes `ms`, `s`, `m`, and bare seconds. Environment parsing splits `RUSTFS_AUDIT_WEBHOOK_ENABLE_PRIMARY` into field `ENABLE` and instance `PRIMARY` at the last underscore.

## State and Persistence Behavior
No shared state or persistence is used. The file creates temporary KVS maps and parses literal strings.

## Dependencies and Integration Points
The tests reflect contracts consumed by `TargetPluginRegistry::create_targets_from_config` through `AuditRegistry`. URL validation uses the `url` crate. Field naming aligns with audit webhook and MQTT plugin expectations in `rustfs_targets`/audit factory code.

## Risks and Edge Cases
The tests validate conventions rather than invoking actual parser code for most cases, so they can drift from implementation. Duration behavior truncates `1000ms` to one second and would treat subsecond millisecond values as `Duration::from_millis`, but only seconds are asserted. FTP is noted as syntactically valid but likely unsupported. Environment variable parsing with fields containing underscores depends on splitting at the last underscore.

## Test Signals
Passing tests signal stable config field vocabulary, audit section prefixes (`audit_webhook`, `audit_mqtt`), env prefix construction (`RUSTFS_AUDIT_*`), merge precedence, accepted duration suffixes, basic URL syntax handling, and MQTT QoS limited to 0, 1, or 2.
