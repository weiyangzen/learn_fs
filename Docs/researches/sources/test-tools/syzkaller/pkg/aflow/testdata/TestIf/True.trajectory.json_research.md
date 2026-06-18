# sources/test-tools/syzkaller/pkg/aflow/testdata/TestIf/True.trajectory.json

Purpose: minimal golden trajectory for a statically true conditional path.

Important structure: 6 spans total: flow, `If`, and `if-body` start/finish pairs. Final result is `{"Done":"done"}`.

Control flow: the true condition executes the body once and closes the wrapper action.

State and persistence: persistent deterministic fixture.

Dependencies and integration: consumed by `If` tests through `testFlow`.

Risks and test signals: catches regressions in the basic true branch path, final result extraction, and body span naming.
