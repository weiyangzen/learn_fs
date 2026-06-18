# sources/test-tools/syzkaller/pkg/compiler/fuzz.go

Purpose: Go fuzz entrypoint for the syzlang compiler.

Important APIs/types/functions: `Fuzz`, `fuzzTarget`, and `fuzzConsts`.

Control flow: `Fuzz` parses arbitrary bytes with a no-op error handler. If parsing succeeds, it compiles the description against a test target and small constant map. It returns 1 only when compilation succeeds.

State and persistence behavior: No persistence. Uses package-level test target and const map.

Dependencies/integration points: Integrates `pkg/ast`, `Compile`, and `targets.Get` for `TestOS/TestArch64`.

Risks: Fuzz constants are intentionally small and may not cover all const-sensitive compiler branches. The no-op error handler suppresses diagnostics by design.

Test signals: Called by `TestFuzz` with regression seeds and suitable for external fuzzing.
