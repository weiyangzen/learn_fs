# sources/test-tools/syzkaller/pkg/aflow/llm_tool.go

## Purpose

`llm_tool.go` implements an LLM-backed tool: a parent `LLMAgent` can call a tool whose implementation is another `LLMAgent` with its own prompt, tools, and context. This enables sub-research without polluting the parent conversation window.

## Important APIs, Types, and Functions

`LLMTool` exposes fields similar to `LLMAgent`: `Name`, `Model`, `TaskType`, `Description`, `Instruction`, and inner `Tools`. `declaration` returns a GenAI function schema accepting `llmToolArgs.Question` and returning `llmToolResults.Answer`. `execute` runs the inner agent. Constants `llmToolPrompt` and `llmToolReply` are temporary state keys. `verify` constructs and verifies the inner agent.

## Control Flow

When invoked, `execute` converts args, writes the question into `ctx.state[AFLOW_LLMTOOL_PROMPT]`, runs the prepared inner agent, deletes the prompt key, reads and deletes `AFLOW_LLMTOOL_REPLY`, and returns it as `Answer`. Verification prebuilds the inner `LLMAgent` with prompt `{{.AFLOW_LLMTOOL_PROMPT}}`, reply key `AFLOW_LLMTOOL_REPLY`, and the configured instruction/tools.

## State and Persistence Behavior

The tool temporarily mutates workflow state with reserved keys and cleans them up. The inner agent may use normal LLM cache and trajectory spans. `verify` stores the constructed inner agent on the `LLMTool` object for later execution.

## Dependencies and Integration Points

It depends on GenAI function declarations, aflow schema conversion, and the `LLMAgent` runtime. It can be included in any parent agent's `Tools` list.

## Risks and Edge Cases

Reserved state keys could conflict with user-defined workflow fields if not treated as internal. If the inner agent fails to set `AFLOW_LLMTOOL_REPLY`, execution errors. The parent context state is shared, so inner tools can see existing workflow state according to their `State` types.

## Test Signals

No direct tests are in this file set, but general tool and LLM agent tests cover the underlying execution primitives.
