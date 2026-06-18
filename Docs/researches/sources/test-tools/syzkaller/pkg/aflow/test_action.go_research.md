# sources/test-tools/syzkaller/pkg/aflow/test_action.go

Purpose: helper for unit-testing a single aflow `Action` without registering a full `Flow`.

Important APIs/functions: `TestAction` accepts an action, workdir, initial args, expected results, and expected error. It depends on the action implementing a private `testVerify` helper interface that returns verified state, expected results, and an output extraction function.

Control flow: creates a verification context, asks the action to verify/prepare test state, finalizes verification, builds a minimal `Context` with state, workdir, no-op event callback, and real-time stub, then executes the action. It compares either the error string or extracted outputs.

State and persistence: all state is in-memory except the caller-supplied workdir. `ctx.Close` is deferred to release context resources.

Dependencies and integration: uses `testing`, `time`, `trajectory`, and testify. It integrates with action implementations that expose test-only verification hooks.

Risks and test signals: the helper intentionally initializes only fields needed by current action tests, so actions requiring cache, context cancellation, or richer stubs need additional setup. Exact string comparison catches error regressions but can be brittle.
