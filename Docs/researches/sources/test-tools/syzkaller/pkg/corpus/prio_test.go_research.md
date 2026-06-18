# sources/test-tools/syzkaller/pkg/corpus/prio_test.go

Purpose: Statistical tests for program selection priorities and focus-area weights.

Important APIs/types/functions: `TestChooseProgram` and `TestFocusAreas`.

Control flow: `TestChooseProgram` builds 1000 inputs with varying signal sizes, samples 1000 choices, and checks observed counts against expected priority probabilities within an epsilon. `TestFocusAreas` creates three weighted focus areas, fills each with programs covering selected PCs, samples 10000 choices, and asserts counts near 10/30/60 percent.

State and persistence behavior: In-memory corpus and random sources only.

Dependencies/integration points: Uses helper generators from `corpus_test.go`, `prog` targets, and `testify/assert`.

Risks: Statistical tests can be flaky if tolerances are too tight or RNG behavior changes. The whole-corpus test includes zero-signal cases mapped to priority 1 but records expected priority as `len(signal)`, which is worth reviewing against `saveProgram` fallback behavior.

Test signals: Provides distribution-level confidence for selection algorithms and focus-area weighting.
