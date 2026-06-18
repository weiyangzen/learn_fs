# sources/test-tools/syzkaller/pkg/corpus/prio.go

Purpose: Weighted random selection of corpus programs, including optional focus-area weighted selection.

Important APIs/types/functions: `ProgramsList`, `chooseProgram`, `saveProgram`, `Corpus.ChooseProgram`, and `Corpus.Programs`.

Control flow: `saveProgram` assigns priority equal to signal size, falling back to 1, and appends cumulative priority. `chooseProgram` samples an integer from cumulative priority and binary-searches `accPrios`. `ChooseProgram` optionally picks a non-empty focus area by configured weights and samples within it, otherwise samples the whole corpus.

State and persistence behavior: `ProgramsList` stores in-memory program slices and cumulative priorities. `ChooseProgram` reads under corpus lock.

Dependencies/integration points: Used by fuzzing mutation scheduling. Depends on `signal.Signal`, `prog.Prog`, and caller-provided `rand.Rand`.

Risks: `chooseProgram` calls `Int63n(pl.sumPrios + 1)`, making zero a possible value and slightly biasing the first program because `accPrios[0] >= 0` is always true. Focus-area selection loop assigns `randArea` whenever `val >= currSum`, effectively ending with the last area whose prefix is below `val`; this works for positive weights but should be reviewed for zero/negative weights.

Test signals: `prio_test.go` statistically checks whole-corpus priority distribution and focus-area weight distribution.
