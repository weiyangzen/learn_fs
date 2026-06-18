# sources/storage-engines/foundationdb/bindings/java/src/test/com/apple/foundationdb/test/StackOperation.java

Purpose: enum contract for non-directory operations in the Java binding stack-machine tests.

Important APIs and flow: constants cover stack commands, waits/threads, transaction lifecycle, mutation commands, explicit conflict range/key operations, reads/ranges/key selectors, version APIs, error retry, arithmetic/concat, tuple and versionstamp packing, float/double encoding, unit-test smoke operations, and stack logging. `StackTester` and `AsyncStackTester` dispatch with `StackOperation.valueOf(inst.op)`.

State and persistence: no runtime state. Dependencies are semantic rather than code-level: tuple-encoded test instructions must match these names exactly after suffix removal by `Instruction`. Risks are compatibility drift across bindings and unimplemented operations causing hard failures. Signal comes from cross-binding generated stack workloads.
