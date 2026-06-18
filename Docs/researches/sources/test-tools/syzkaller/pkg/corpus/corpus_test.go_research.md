# sources/test-tools/syzkaller/pkg/corpus/corpus_test.go

Purpose: Tests for corpus save/update, coverage aggregation, stats, and concurrent access.

Important APIs/types/functions: `TestCorpusOperation`, `TestCorpusCoverage`, `TestCorpusSaveConcurrency`, `generateInput`, `generateRangedInput`, and `getTarget`.

Control flow: Tests generate programs for the test target, save them to monitored or plain corpus instances, read update events, check `Exists` and `NewCover`, query items and stats, call `Minimize`, and run concurrent goroutines that save and choose programs.

State and persistence behavior: Uses in-memory corpus state and channels. No disk writes.

Dependencies/integration points: Exercises `prog.Target.Generate`, signal creation, corpus APIs, and target lookup.

Risks: `TestCorpusSaveConcurrency` starts goroutines but does not wait for them, so it is more of a race/smoke trigger than deterministic completion test. Running with the race detector would add value.

Test signals: Covers event semantics, aggregate signal/coverage stats, item lookup, minimization entrypoint, and basic concurrent lock safety.
