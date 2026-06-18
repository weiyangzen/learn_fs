# sources/test-tools/syzkaller/pkg/aflow/testdata/TestIf/BoolTrue.trajectory.json

Purpose: golden trajectory for an `If` action with a boolean true condition.

Important structure: 6 spans total: flow start/finish, `If` action start/finish, and `if-body` action start/finish. Final result is `{"Done":"done"}`.

Control flow: `If` receives `Cond: true`, executes `if-body`, and then closes the wrapper action.

State and persistence: persistent golden data with deterministic timestamps, the boolean argument, and body result.

Dependencies and integration: validates `If` truthiness and nested action span emission under the runner harness.

Risks and test signals: catches regressions where condition args are not logged, true branch nesting changes, or body output stops propagating to flow outputs.
