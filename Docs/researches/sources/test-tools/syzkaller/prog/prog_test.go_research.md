## sources/test-tools/syzkaller/prog/prog_test.go

Purpose: broad integration tests for generation, default arguments, serialization round trips, VMA length handling, target attributes, cross-target deserialization, special type generators, path safety, fallback signal generation, sanitization, and recursion pruning.

Important APIs/types/functions: `TestGeneration`, `TestDefault`, `TestDefaultCallArgs`, `testSerialize`, `TestVmaType`, `TestFsckAttr`, `TestCrossTarget`, `testCrossTarget`, `testCrossArchProg`, `TestSpecialStructs`, `TestEscapingPaths`, `TestFallbackSignal`, `TestSanitizeRandom`, and `TestPtrRecursion`.

Control flow: tests use target initialization helpers, generate or deserialize programs, serialize/deserialize them in strict and non-strict modes, mutate/minimize for cross-target validation, and verify expected syscall/argument behavior.

State and persistence: no persistence. Tests exercise generated in-memory target state and program graphs.

Dependencies/integration: integrates with all registered targets, target-specific special generators, fallback signal code, minimization, mutation, and serializer/deserializer.

Risks: cross-target testing is O(N^2) in argument count and filters large programs. Some tests skip under race mode or reduce iterations in short mode. Expected serialization can be sensitive to description changes.

Test signals: high-value smoke and regression coverage across the `prog` package and target registry.
