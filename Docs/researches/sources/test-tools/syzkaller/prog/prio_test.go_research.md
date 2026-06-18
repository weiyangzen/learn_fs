## sources/test-tools/syzkaller/prog/prio_test.go

Purpose: validates priority normalization, static resource-based priority calculation, deterministic choice-table behavior, and performance.

Important APIs/types/functions: `TestNormalizePrios`, `TestStaticPriorities`, `TestPrioDeterminism`, and `BenchmarkBuildChoiceTable`.

Control flow: tests build small priority matrices or target choice tables, run normalization/calculation, and compare expected weights or repeated outputs under identical seeds.

State and persistence: in-memory only. Random sources are deterministic for reproducibility.

Dependencies/integration: relies on test target metadata and `BuildChoiceTable`.

Risks: deterministic tests guard ordering and random choice stability, but they do not prove priority quality for fuzzing effectiveness.

Test signals: useful for catching accidental changes to normalization math, enabled-call filtering, and map-order nondeterminism.
