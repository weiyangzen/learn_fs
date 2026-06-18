# sources/test-tools/syzkaller/pkg/aflow/testdata/TestIf/IntTrue.trajectory.json

Purpose: golden trajectory for integer condition truthiness where non-zero is true.

Important structure: 6 spans total: flow, `If`, and `if-body` start/finish pairs. Final result is `{"Done":"done"}`.

Control flow: non-zero integer condition executes the body and propagates its result.

State and persistence: persistent span/result fixture for the runner.

Dependencies and integration: validates condition coercion used by the aflow `If` action.

Risks and test signals: detects regressions in truthiness for numeric conditions or nested body span emission.
