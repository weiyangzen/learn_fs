# sources/test-tools/syzkaller/pkg/aflow/testdata/TestIf/BoolFalse.trajectory.json

Purpose: golden trajectory for an `If` action with a boolean false condition and no else branch.

Important structure: 4 spans total: flow start/finish and `If` action start/finish. Final result is `{"Done":""}`.

Control flow: `If` receives `Cond: false`, records only the wrapper action, and does not execute `if-body`.

State and persistence: persistent golden fixture containing deterministic timestamps and serialized `If` args.

Dependencies and integration: consumed by `If` tests through `testFlow`; validates false boolean truthiness and default empty output behavior.

Risks and test signals: catches regressions that execute the body on false, drop wrapper args, or omit zero-valued output fields.
