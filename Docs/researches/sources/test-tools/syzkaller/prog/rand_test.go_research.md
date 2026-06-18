## sources/test-tools/syzkaller/prog/rand_test.go

Purpose: validates random generation and mutation determinism, filename sandbox safety, enabled-call enforcement, integer bit bounds, flags distribution visibility, truncation, and `NoGenerate` behavior.

Important APIs/types/functions: `TestNotEscaping`, `TestDeterminism`, `generateProg`, `TestEnabledCalls`, `TestSizeGenerateConstArg`, `TestFlags`, `TestTruncateToBitSize`, and `TestNoGenerate`.

Control flow: deterministic tests replay the same seed through generation, mutation, hints, minimization, serialization, and deserialization. Enabled/no-generate tests build restricted choice tables and verify generated/mutated programs stay within allowed syscall sets.

State and persistence: in-memory only. Deterministic seeds and generated corpus lists are local to tests.

Dependencies/integration: depends on hint mutation, minimization, serialization, deserialization, target choice tables, and test target setup.

Risks: distribution tests mostly log observations instead of asserting exact ratios. Determinism checks can be sensitive to map iteration unless production code sorts keys, which this subset generally does.

Test signals: strong coverage for random-source reproducibility and safety constraints that protect fuzzing runs from invalid programs.
