# sources/test-tools/syzkaller/pkg/aflow/testdata/TestDoWhile.trajectory.json

Purpose: golden trajectory for `TestDoWhile`, recording a successful do-while repair loop that needs three iterations before the condition clears.

Important structure: 22 spans total: 2 flow spans, 2 loop spans, 6 iteration spans, and 12 action spans. Names include `test`, loop iterations `0`, `1`, `2`, `patch-generator`, and `patch-tester`.

Control flow: the flow starts, enters a loop, and records three iterations. The first two iterations produce `Patch: bad`; `patch-tester` returns empty `Diff` and `TestError: error`, so the loop continues. The third iteration produces `Patch: good`; `patch-tester` returns `Diff: diff` and empty `TestError`, causing loop exit.

State and persistence: this JSON is persistent golden state consumed by `runner_test.go`. It stores deterministic stub timestamps and serialized action results, not runtime cache data.

Dependencies and integration: generated from `loop_test.go` via `testFlow` and compared with `osutil.ReadJSON`. It exercises `DoWhile` span emission and output extraction.

Risks and test signals: any change to loop span nesting, action result fields, timestamp stubbing, or exit condition semantics will fail the golden comparison. Final flow result is `{"Diff":"diff"}`.
