# sources/test-tools/syzkaller/pkg/aflow/testdata/TestLLMTool.llm.json

Purpose: golden record of LLM requests emitted by `TestLLMTool`, including main-agent calls, nested sub-agent calls, function-call history, and config changes.

Important structure: JSON array of request records with `Model`, optional `Config`, and `Request`. The first request targets `model` with a tool declaration for `researcher`; nested requests target `sub-agent-model` with a tool declaration for `researcher-tool`. Repeated configs are omitted by the harness unless changed.

Control flow: the request history starts with the main prompt, then records the sub-agent prompt `What do you think?`, then the function-call/function-response turn for `researcher-tool`. Later records repeat the pattern for `But really?`, include additional subtool calls, and preserve the request chain around the simulated token overflow before final completion.

State and persistence: persistent golden fixture for serialized `genai.GenerateContentConfig` and content requests. It stores schemas, tool descriptions, system instructions, thinking config, and conversation turns.

Dependencies and integration: produced and consumed by `runner_test.go` for `TestLLMTool`; tied to `llm_tool_test.go`, schema generation, and GenAI request formatting.

Risks and test signals: highly sensitive to config serialization, tool schema generation, default instruction text, request history pruning, and function-call response formatting. It is the best signal for nested LLM tool API compatibility.
