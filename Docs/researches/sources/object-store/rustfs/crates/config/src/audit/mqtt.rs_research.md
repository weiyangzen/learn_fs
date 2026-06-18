# sources/object-store/rustfs/crates/config/src/audit/mqtt.rs

## Purpose
Declares MQTT audit target environment variables and config keys, including reconnect, keepalive, queue, TLS, and websocket path allowlist settings.

## Important APIs, types, and functions
Exports `ENV_AUDIT_MQTT_*`, `ENV_AUDIT_MQTT_KEYS`, and `AUDIT_MQTT_KEYS`. Config keys include broker, topic, QoS, username/password, reconnect/keepalive intervals, queue directory/limit, TLS policy/material, trust-leaf-as-CA, websocket path allowlist, and comments.

## Control flow
No runtime control flow; consumers iterate the static slices.

## State and persistence behavior
All values are compile-time string constants.

## Dependencies and integration points
Depends on shared MQTT key constants from the crate root and is re-exported by audit aggregation. MQTT audit publisher setup should consume these constants.

## Risks and edge cases
The env key slice omits `COMMENT_KEY` by design while config keys include it. QoS, TLS policy, and websocket allowlist are not validated here. Manual array length maintenance is required.

## Test signals
No local tests; parser integration should verify every key is accepted and values are validated downstream.
