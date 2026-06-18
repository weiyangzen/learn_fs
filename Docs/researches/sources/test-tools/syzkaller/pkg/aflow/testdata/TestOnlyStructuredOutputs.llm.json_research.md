<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/testdata/TestOnlyStructuredOutputs.llm.json -->
# Research: sources/test-tools/syzkaller/pkg/aflow/testdata/TestOnlyStructuredOutputs.llm.json

## Purpose
This fixture backs `TestOnlyStructuredOutputs`. It records the initial model request for an agent that has structured outputs only and no text `Reply` field.

## Important APIs, Types, and Functions
It exercises `LLMOutputs`, the synthetic `set-results` tool, `llmOutputsInstruction`, and schema generation for a `Result int` output. It uses `LLMAgent` without a reply variable.

## Control Flow
The JSON array contains 1 request. The request includes the system instruction `Instruction` plus the set-results requirement, a single function declaration named `set-results`, and the initial user prompt. The mocked model response in the test is a `set-results` call with `Result: 42`.

## State and Persistence
The file persists request config, not execution state. It establishes that structured output agents still run as text-capable model calls with a function tool and that final state is expected to come from tool results rather than a model text reply.

## Dependencies and Integration Points
It integrates with the genai tool declaration schema, aflow output registration, and final result extraction in `LLMAgent.execute`. The corresponding trajectory records that no final reply text is required.

## Risks
If agent verification starts requiring `Reply` even when `Outputs` is set, this fixture fails. If set-results schema generation changes, the golden request changes.

## Test Signals
The important signal is a single request declaring only `set-results` with required integer `Result`, thinking level `HIGH`, and no tool responses yet.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/testdata/TestOnlyStructuredOutputs.llm.json -->
