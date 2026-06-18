## sources/test-tools/syzkaller/prog/test/fuzz.go

Purpose: provides fuzz entry points for deserialization and log parsing using the syzkaller test target.

Important APIs/types/functions: `FuzzDeserialize`, `FuzzParseLog`, and package-level `fuzzTarget`/`fuzzChoiceTable`.

Control flow: `FuzzDeserialize` tries non-strict and strict deserialization, verifies non-strict is not stricter than strict, checks serialize/deserialize idempotence, clone equality, optional exec serialization/deserialization, and then mutates the program. `FuzzParseLog` returns 1 if arbitrary data yields any parsed log entries.

State and persistence: no persistence. The target and choice table are initialized once at package load.

Dependencies/integration: imports all sys targets for registration, uses `targets.TestOS/TestArch64`, serialization, exec serialization, clone, mutation, and parse-log code.

Risks: fuzzing intentionally feeds malformed inputs and panics on invariant violations. Return value from `FuzzParseLog` is a fuzzer signal, not a correctness result for production callers.

Test signals: `fuzz_test.go` seeds known edge cases for malformed programs, large auto lengths, ANY values, recursive resources, and parse-log inputs.
