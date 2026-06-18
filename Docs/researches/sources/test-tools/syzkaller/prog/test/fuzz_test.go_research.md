## sources/test-tools/syzkaller/prog/test/fuzz_test.go

Purpose: regression seeds for the fuzz entry points in `prog/test/fuzz.go`.

Important APIs/types/functions: `TestFuzz`.

Control flow: iterates over a list of malformed or edge-case program strings, logs the case index, converts each to a full-slice byte input, and runs both `FuzzDeserialize` and `FuzzParseLog`.

State and persistence: no persistence.

Dependencies/integration: depends on the fuzz package target initialization and deserializer/mutator invariants.

Risks: seed strings are compact reproductions for prior parser or mutation failures; future serializer grammar changes may require updating them.

Test signals: useful smoke coverage for previously risky malformed inputs, including unterminated pointers, invalid escapes, huge AUTO lengths, ANY blobs, repeated resources, and recursion.
