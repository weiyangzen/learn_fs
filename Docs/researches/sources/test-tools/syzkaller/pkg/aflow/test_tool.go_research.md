# sources/test-tools/syzkaller/pkg/aflow/test_tool.go

Purpose: helper utilities for testing aflow `Tool` implementations and fuzzing tool execution.

Important APIs/types/functions: `TestToolOption`, `testToolContext`, `TestTool`, `TestErrorPrefix`, `TestWorkdir`, and `FuzzTool`. `TestTool` requires tools to implement a private `testVerify` helper; `FuzzTool` requires `checkFuzzTypes`.

Control flow: `TestTool` builds and finalizes a verification context, checks the declaration path does not crash, applies optional context modifiers, executes the tool, validates exact or prefix error text, ensures expected tool errors are `badCallError`, and runs the result checker. `FuzzTool` converts fuzz input into state/args and executes against a minimal context.

State and persistence: test state lives in a minimal `Context`; workdir is optional via `TestWorkdir`. No persistent writes are done by the helper itself.

Dependencies and integration: imports `errors`, `strings`, `testing`, and testify. It integrates with all tool tests needing consistent verification/execution checks and bad-call semantics.

Risks and test signals: minimal context setup may hide dependencies until a tool needs cache/workdir/stubs. The bad-call assertion is a strong signal that user/LLM input validation remains distinct from infrastructure failures.
