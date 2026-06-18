# sources/test-tools/syzkaller/tools/syz-imagegen/combinations_test.go

Purpose: this Linux-only test file locks down the expected output of `CoveringArray`.

Important APIs and flow: `TestFullCombinations` checks empty input, a single-value three-parameter case, and full binary cartesian expansion when `n == 0`. `TestPairCombinations` checks the current greedy bounded output for three binary parameters and `n == 4`.

State and persistence: no state; pure tests.

Dependencies and integration: uses `testify/assert`.

Risks: bounded covering arrays can have multiple valid answers; the test intentionally pins the current algorithm's deterministic output to catch accidental changes.

Test signals: direct regression signal for imagegen flag enumeration stability.
