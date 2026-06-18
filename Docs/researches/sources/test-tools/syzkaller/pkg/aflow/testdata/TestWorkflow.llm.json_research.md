# sources/test-tools/syzkaller/pkg/aflow/testdata/TestWorkflow.llm.json

## Purpose
Comprehensive golden LLM request fixture for a multi-step aflow workflow with tools, result-setting, candidate agents, and aggregation.

## Important Data and APIs
The array contains eight model request snapshots across `model1`, `model2`, and `model3`. Config sections include generated tool declarations for `tool1`, `tool2`, and `set-results`, thinking config, temperature, and instruction prompts. Request histories include function call and function response parts.

## Control Flow
The fixture models an action feeding an agent prompt, tool calls and tool responses, structured result setting, multiple candidate-agent calls, and an aggregation prompt that sees candidate replies.

## State and Persistence Behavior
It persists request history used by deterministic tests. Conversation state is captured by appending model/tool turns rather than by any runtime store.

## Dependencies and Integration Points
Integrated with aflow workflow tests, schema generation, genai serialization, and agent-candidate orchestration.

## Risks and Test Signals
Any change in prompt text, tool schema ordering, function-response shape, or candidate aggregation order will surface through exact fixture mismatch. It is a broad regression signal for workflow-to-LLM request construction.
