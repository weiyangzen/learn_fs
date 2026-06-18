# sources/test-tools/syzkaller/pkg/aflow/testdata/TestValidatedLLMOutputs.llm.json

## Purpose
Golden LLM request fixture for validation of structured LLM outputs. It captures model calls that include a synthetic `set-results` function declaration and retry context after an invalid result.

## Important Data and APIs
The top-level array stores two request snapshots with `Model`, optional `Config`, and `Request`. The config includes system instruction text, tool schemas, response modality, temperature, and thinking config. The tool schema validates a required integer `Result` field and mirrors aflow's JSON schema generation.

## Control Flow
The first request sends the initial prompt with the result-setting tool available. The second request includes prior conversation and verification feedback so the model can correct output after the validator rejects a result.

## State and Persistence Behavior
Persistent test fixture only. It stores serialized LLM requests, not responses or live state.

## Dependencies and Integration Points
Used by aflow tests for LLM validation/retry behavior and by genai request serialization code. It depends on exact schema names and generated JSON schema layout.

## Risks and Test Signals
Schema churn, instruction text changes, or altered retry prompts will break exact comparisons. The fixture is a high-signal regression check for validator-tool wiring and request history preservation.
