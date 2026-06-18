# sources/test-tools/syzkaller/pkg/aflow/testdata/TestForEach/UnexportedOutput.trajectory.json

Purpose: golden trajectory for a `ForEach` scenario involving an action output that is internal/unexported from the final flow output.

Important structure: 16 spans total: 2 flow, 2 loop, 4 iteration, and 8 action spans. Names include `ForEach`, iterations `0` and `1`, `process-item`, and `consume-hidden`.

Control flow: each of two iterations runs `process-item` and then `consume-hidden`. The final exported result is `{"Result":["A","B"]}`, while intermediate hidden output is consumed within the loop body rather than exported.

State and persistence: persistent golden file records action-level results and final exported outputs. It verifies loop body internal state can be passed between actions without appearing in final outputs.

Dependencies and integration: consumed by a `TestForEach/UnexportedOutput` subtest in the aflow suite.

Risks and test signals: detects changes in output-use verification, unexported/intermediate state handling, and loop body span nesting.
