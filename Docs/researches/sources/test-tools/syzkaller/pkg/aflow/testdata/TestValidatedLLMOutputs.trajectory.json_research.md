# sources/test-tools/syzkaller/pkg/aflow/testdata/TestValidatedLLMOutputs.trajectory.json

## Purpose
Golden trajectory for structured-output validation where the first `set-results` call returns an unacceptable value and a later call succeeds.

## Important Data and APIs
The file follows `trajectory.Span` JSON and covers flow, agent, llm, and tool spans. Tool spans carry `Result` arguments/results and the validation error text `result cannot be 42`.

## Control Flow
Execution starts the flow and agent, records an LLM turn, executes `set-results` with invalid output, records another LLM retry, executes `set-results` with corrected output, then closes the agent and flow.

## State and Persistence Behavior
It is immutable testdata representing event chronology. The only state transition encoded is validator failure followed by successful result capture.

## Dependencies and Integration Points
Integrated with aflow validated-output tests, span serialization, and downstream trajectory renderers.

## Risks and Test Signals
The important risks are unstable error text, changed retry sequencing, or missing tool results on error spans. Exact fixture comparison catches those regressions.
