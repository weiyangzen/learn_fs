# sources/test-tools/syzkaller/pkg/aflow/llm_agent.go

## Purpose

`llm_agent.go` implements aflow's LLM action runtime. It formats prompts, configures Gemini/Vertex requests, executes iterative tool-calling chats, handles structured outputs, validates/fixes replies, supports multiple candidates, compresses long histories, detects tool-call loops, caches model responses, and classifies retry/quota/token errors.

## Important APIs, Types, and Functions

Core types are `LLMAgent`, `agentSession`, `TaskType`, `Tool`, `llmReply`, and `llmOutputs`. Public helpers include `Tools`, `LLMReply`, `LLMOutputs`, and `ValidatedLLMOutputs`. Execution paths are `execute`, `executeMany`, `executeOne`, `chat`, `callTools`, `checkFinalReply`, `generateContent`, and `generateContentCached`. History management is `slide`, `maybeCompressContext`, and `compressContext`. Error handling is `parseLLMError`, `parseLLMResp`, `llmBackoffDuration`, and retry/overflow/quota types. Verification is in `LLMAgent.verify` and `verifyTemplate`. Loop detection is `recordAndCheckDuplicate`.

## Control Flow

Execution builds config/instruction/prompt/tools from current state, starts an agent span, and opens an `agentSession` with a user prompt. Each chat iteration may compress history, starts an LLM span, applies sliding-window summary hints, sends a cached model request, parses reply/thoughts/function calls, appends model content to history, and either validates final reply/results or executes requested tools. Tool calls produce tool spans and function responses; `BadCallError`s are returned to the model, while hard errors abort. Structured outputs require a successful `set-results` call before the final reply unless the agent is output-only. Multiple candidates run `executeOne` repeatedly and aggregate replies/outputs into slices.

## State and Persistence Behavior

Workflow-visible state is updated only after successful agent execution. Per-execution `agentSession` holds request history, tool history, summary pointer, outputs, and answer-now flag. LLM responses are persisted in the aflow cache under `llm` with hashes of model, config, request, and candidate. Model thoughts/tokens/replies are persisted in trajectory spans via `onEvent`.

## Dependencies and Integration Points

It depends on GenAI types, aflow schema/template/verification/cache/trajectory helpers, `osutil.JSONDeepCopy`, and HTTP error codes. Every LLM-based workflow uses this runtime. Tools implement the local `Tool` interface and are declared as GenAI function declarations.

## Risks and Edge Cases

The runtime assumes `resp.Candidates[0]` exists after `parseLLMResp`. Tool-call history must be session-local to avoid false loop detection. Caching model responses means prompt/config hash stability matters. Token compression invokes another model and may lose details despite explicit summary requirements. Sliding-window summary is prompt-based and can accidentally become final reply. `parseLLMErrorImpl` depends on provider message substrings that may change. `verify` mutates default `compressTokens` and validated reply names.

## Test Signals

`llm_agent_test.go`, `func_tool_test.go`, and `flow_test.go` cover retry classification, backoff, token compression, history reset, output overflow thinking reduction, structured outputs, validated outputs/replies, tool prompt variables, bad tool calls, duplicate loops, and registration errors.
