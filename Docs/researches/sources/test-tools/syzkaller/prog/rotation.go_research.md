## sources/test-tools/syzkaller/prog/rotation.go

Purpose: selects a random but dependency-aware subset of syscalls for corpus rotation/focused fuzzing.

Important APIs/types/functions: `Rotator`, `rotatorResource`, `MakeRotator`, `Rotator.Select`, `rotatorState`, `rotatorState.Select`, `addCall`, and `selectCalls`.

Control flow: construction classifies calls by resource inputs/outputs, adds synthetic filename/VMA resources, groups precise/imprecise constructors and uses, and sets a goal capped at 200 calls. Selection starts with resourceless calls, then repeatedly processes top resources and dependency resources, selecting constructors and users with probabilities until transitive enablement reaches the goal.

State and persistence: selection is in-memory and deterministic for a given random source and call set. No persistent state.

Dependencies/integration: depends on resource metadata populated in `resources.go`, `ForeachCallType`, and target transitive enablement.

Risks: probability heuristics can skew coverage. Dependency and top-resource queues need deterministic ordering before shuffling to avoid map-order nondeterminism. Empty resource sets return all calls.

Test signals: `rotation_test.go` checks resourceless behavior, selected subset validity, broad coverage over repeated selections, and determinism.
