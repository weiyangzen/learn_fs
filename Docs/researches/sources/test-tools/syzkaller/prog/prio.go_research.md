## sources/test-tools/syzkaller/prog/prio.go

Purpose: computes syscall-to-syscall priorities used by generation to bias new calls toward combinations likely to produce coverage.

Important APIs/types/functions: `Target.CalculatePriorities`, `prepareEnabledSyscalls`, `calcStaticPriorities`, `calcResourceUsage`, `calcDynamicPrio`, `normalizePrios`, `ChoiceTable`, `BuildChoiceTable`, `ChoiceTable.Generatable`, and `ChoiceTable.choose`.

Control flow: enabled calls are filtered to exclude disabled and `NoGenerate` calls. Static priorities are built from shared resource, pointer, filename, string, and VMA usage. Dynamic priorities count ordered call pairs in corpus programs and dampen counts with square root. Both matrices are normalized to distribute `10 * enabled` points per row, then `ChoiceTable` stores cumulative rows for weighted binary-search selection.

State and persistence: stores only in-memory priority matrices and choice-table cumulative rows. No persistent state.

Dependencies/integration: depends on `ForeachType`, syscall metadata, resource descriptors, corpus programs, and `randGen.generateCall`.

Risks: constants are heuristic and can bias fuzzing quality. Sparse enabled sets can produce rows with low or zero priorities; self-priority fallback handles fully isolated calls. Debug mode checks no disabled call has nonzero priority.

Test signals: `prio_test.go` covers normalization, static priorities, determinism, and benchmarks choice-table construction.
