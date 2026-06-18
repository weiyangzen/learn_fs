# sources/test-tools/syzkaller/pkg/aflow/llm_tool_test.go

Purpose: validates nested LLM tool behavior where a main `LLMAgent` exposes an `LLMTool` named `researcher`, and that sub-agent has its own `researcher-tool` function tool. `TestLLMTool` proves workflow input state reaches the nested function tool, the nested agent can call tools, recover from an input-token-overflow API error, and still return the main `Reply`. `TestLLMToolMaxIters` stresses the sub-agent tool loop up to `maxLLMIterations`.

Important APIs and control flow: both tests use `testFlow`, `LLMAgent`, `LLMTool`, `NewFuncTool`, `genai.Part`, and `genai.FunctionCall`. The fixture sequence alternates main-agent LLM calls, `researcher` tool invocations, sub-agent LLM calls, subtool calls, and final text replies.

State and persistence: no durable state is written by this file. Runtime state is the workflow state map, especially `Input` and `Reply`; request and trajectory persistence is delegated to `runner_test.go` golden files.

Dependencies and integration: depends on `google.golang.org/genai`, `net/http`, `strings`, and testify assertions. It integrates with aflow LLM agent/tool registration, bad API error handling, nested tool schemas, and the golden files `TestLLMTool.llm.json` and `TestLLMTool.trajectory.json`.

Risks and test signals: the main risk is regressions in nested conversation accounting, repeated sub-agent tool calls, or error recovery after token overflow. Strong signals are the assertion that subtool args have expected prefixes, the nested state assertion `Input == 42`, and golden request/trajectory comparison.
