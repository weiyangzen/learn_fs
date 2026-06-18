## sources/test-tools/syzkaller/prog/rotation_test.go

Purpose: verifies syscall rotation correctness, coverage, and deterministic behavior.

Important APIs/types/functions: `TestRotationResourceless`, `TestRotationRandom`, `TestRotationCoverage`, `selectCalls`, and `TestRotationDeterminism`.

Control flow: tests build call sets of varying size, run `MakeRotator(...).Select()`, ensure selected calls are a subset of original calls, repeat selections until all eligible calls are seen, and compare identical-seed outputs.

State and persistence: in-memory maps of syscalls and counters. No persistence.

Dependencies/integration: uses target metadata, resource transitive enablement, deterministic sorting, and `testify/require`.

Risks: coverage test uses 10,000 iterations and can still be probabilistic, though deterministic random sources reduce flakiness. Tests log selected calls for diagnosis.

Test signals: good guard against nondeterministic map iteration and dependency-breaking subset selection.
