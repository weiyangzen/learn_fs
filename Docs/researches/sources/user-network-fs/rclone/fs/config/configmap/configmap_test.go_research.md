# sources/user-network-fs/rclone/fs/config/configmap/configmap_test.go

Purpose: tests the internal behavior of `configmap.Map` and `Simple` encode/decode.

Important APIs/functions: interface assertions for `Simple`; `TestConfigMapGet`, `TestConfigMapSet`, `TestConfigMapGetPriority`, `TestConfigMapClearGetters`, `TestConfigMapClearSetters`, `TestSimpleEncode`, and `TestSimpleDecode`.

Control flow: map tests add getters/setters in different orders and priorities, assert lookup precedence and mutation propagation, then clear by priority or all setters. Encode/decode tests compare exact base64 raw strings and decode whitespace-tolerant inputs, invalid base64, JSON `null`, and invalid JSON.

State and persistence behavior: tests mutate in-memory maps and verify `Map` stores getter/setter references. Encoded strings are stable because JSON map output is expected for the tested keys and used in CLI/token flows.

Dependencies and integration points: uses base64 and `testify`. It constrains behavior used by backend config, config storage overlays, and authorization blob passing.

Risks: map JSON order can be a compatibility concern, though Go's JSON encoder sorts map keys for string keys. No concurrency tests are present.

Test signals: strong coverage for priority and setter semantics plus error-wrapped encode/decode paths.
