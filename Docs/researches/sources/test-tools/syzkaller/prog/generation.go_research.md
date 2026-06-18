# sources/test-tools/syzkaller/prog/generation.go

Purpose: provides the public random program generation entry point.

Important APIs/types/functions: `Target.Generate(rs rand.Source, ncalls int, ct *ChoiceTable) *Prog`.

Control flow and state: creates an empty `Prog`, a `randGen`, and a fresh analysis `state`. It repeatedly calls `generateCall`, analyzes every generated call, and appends calls until at least `ncalls`. If resource-creating helper calls overflow the requested count, it removes calls at `ncalls-1` until count matches, allowing affected resources in the final call to fall back to defaults. Finally it sanitizes/fixes and debug-validates the program.

Dependencies and integration: depends on `newRand`, `newState`, `generateCall`, state analysis, `RemoveCall`, `sanitizeFix`, and `debugValidate`. Used by random tests, fuzzing, mutation tests, checksum tests, and serialization round trips.

Risks: removing overflow helper calls can change resource availability and relies on `RemoveCall` cleanup/defaulting. Generation quality depends on accurate analysis state and choice tables.

Test signals: many tests use `Generate`; random serialization, checksum, conditional, hints, minimization, and executor tests indirectly stress this path.
