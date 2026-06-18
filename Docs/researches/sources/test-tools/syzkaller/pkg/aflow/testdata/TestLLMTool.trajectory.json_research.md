# sources/test-tools/syzkaller/pkg/aflow/testdata/TestLLMTool.trajectory.json

Purpose: golden trajectory for `TestLLMTool`, showing nested agent/tool execution and recovery from a model input-token overflow.

Important structure: 36 spans total: 2 flow, 6 agent, 18 llm, and 10 tool spans. Names include `test`, main agent `smarty`, sub-agent/tool `researcher`, and nested `researcher-tool`.

Control flow: the main agent starts and calls the `researcher` tool with `What do you think?`. That tool starts a sub-agent, which calls `researcher-tool` and returns `Nothing.`. The main agent then calls `researcher` again with `But really?`; the sub-agent calls its tool multiple times, records an API error for token overflow, continues, returns `Still nothing.`, and the main agent finally returns `YES`.

State and persistence: persistent golden span fixture with deterministic timestamps, prompts, instructions, args, results, and the serialized API error. Final flow result is `{"Reply":"YES"}`.

Dependencies and integration: consumed by `llm_tool_test.go` through `testFlow`; validates `LLMAgent`, `LLMTool`, nested tool execution, trajectory emission, and error propagation/continuation.

Risks and test signals: strong signal for span nesting, nested agent prompt/instruction formatting, tool result shape, and API error handling. It will fail on harmless but intentional changes to wording, ordering, or request loop behavior.
