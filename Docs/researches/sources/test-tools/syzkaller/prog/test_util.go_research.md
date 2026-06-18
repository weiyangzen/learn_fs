## sources/test-tools/syzkaller/prog/test_util.go

Purpose: shared testing helpers for target initialization and deserialization table tests.

Important APIs/types/functions: `InitTargetTest`, `DeserializeTest`, and `TestDeserializeHelper`.

Control flow: `InitTargetTest` marks tests parallel and retrieves a target. `TestDeserializeHelper` runs each case under non-strict and strict modes, checks expected errors, optionally transforms the program, compares compact or verbose serialization to expected output, and verifies exec serialization does not fail.

State and persistence: no persistence. Test cases are local data structures.

Dependencies/integration: depends on target registry, deserializer modes, serializer variants, and `SerializeForExec`.

Risks: helper runs subtests in parallel through target init; target lazy init must be concurrency-safe. Expected output can match either verbose or non-verbose serialization to support strict-mode syntax.

Test signals: many package tests rely on this helper, so it amplifies coverage for deserialization, transformation, serialization, and exec encoding.
