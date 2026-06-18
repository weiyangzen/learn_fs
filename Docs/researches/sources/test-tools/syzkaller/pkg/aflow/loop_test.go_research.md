# sources/test-tools/syzkaller/pkg/aflow/loop_test.go

Purpose: tests `DoWhile` and `ForEach` registration, verification, execution, state propagation, and golden trajectory output.

Important APIs/functions: uses `testFlow`, `testRegistrationError`, `Pipeline`, `NewFuncAction`, `DoWhile`, and `ForEach`. Local struct types model action inputs/results such as patch generation, patch testing, list item processing, and loop continuation variables.

Control flow: `TestDoWhile` simulates patch generation until a tester clears `TestError` on the third iteration. `TestDoWhileErrors` verifies missing inputs, empty `While`, unused outputs, and invalid `MaxIterations`. `TestDoWhileMaxIters` expects the max-iteration error path. `TestForEach` builds a slice accumulator by uppercasing items. `TestForEachErrors` covers missing names, missing list input, non-slice list, and unused item variable. Nested-loop tests assert inner loop outputs do not panic on re-entry, remain visible to later outer actions, and cannot redefine variables already created outside a loop.

State and persistence: tests mutate only in-memory state and rely on `testFlow` to compare trajectories against files under `testdata`.

Dependencies and integration: imports `fmt`, `strings`, and `testing`; integrates directly with loop verification in `loop.go` and function-action registration in aflow.

Risks and test signals: strong regression signals are exact registration error strings and golden span comparisons. The nested-loop cases are especially important because loop verification deliberately bends normal defined-before-use rules.
