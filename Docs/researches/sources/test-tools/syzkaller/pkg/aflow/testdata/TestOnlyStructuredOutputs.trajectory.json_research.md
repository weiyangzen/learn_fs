<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/testdata/TestOnlyStructuredOutputs.trajectory.json -->
# Research: sources/test-tools/syzkaller/pkg/aflow/testdata/TestOnlyStructuredOutputs.trajectory.json

## Purpose
This trajectory is the execution golden for `TestOnlyStructuredOutputs`. It proves that a pure structured-output agent can complete without producing text.

## Important APIs, Types, and Functions
It records spans for `LLMAgent`, the synthetic `set-results` tool from `LLMOutputs`, and final flow result collection. The central state field is `outputs map[string]any` inside the agent session.

## Control Flow
The file has 8 spans: 2 flow, 2 agent, 2 LLM, and 2 tool spans. The model calls `set-results`, the tool returns `Result: 42`, the agent finishes without a reply string, and the flow exports `Result: 42`.

## State and Persistence
The span results persist `Result: 42` at the tool, agent, and flow levels. This protects the behavior that `Outputs` can satisfy final workflow outputs independently from `Reply`.

## Dependencies and Integration Points
It is paired with the `.llm.json` request fixture and depends on `trajectory.Span.Results` serialization for tool and flow outputs. It also depends on the synthetic set-results tool being treated like a normal tool span.

## Risks
A regression could require a text reply, drop structured outputs when no reply exists, or fail to record set-results as a tool span. All would change this trajectory.

## Test Signals
Expected signals are no span errors, no final reply text, and final results `{"Result":42}`.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/testdata/TestOnlyStructuredOutputs.trajectory.json -->
