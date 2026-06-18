<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/testdata/TestNilToolArg.llm.json -->
# Research: sources/test-tools/syzkaller/pkg/aflow/testdata/TestNilToolArg.llm.json

## Purpose
This LLM request fixture backs `TestNilToolArg` in `llm_agent_test.go`. It captures how an `LLMAgent` declares and replays a function tool whose argument is a nullable pointer field.

## Important APIs, Types, and Functions
The fixture records mocked `genai.GenerateContent` inputs produced by `LLMAgent.execute`, `NewFuncTool`, schema generation, and function response handling. The tool is `swiss-knife`; its `Optional` parameter schema has type `["null","integer"]` and is listed as required.

## Control Flow
The array has 2 requests. The first request contains the model config, system instruction with rendered `{{.toolSwissKnife}}`, and a `swiss-knife` function declaration. The second request replays the prompt, a model function call with `"Optional": null`, and a function response reporting `missing argument "Optional"`.

## State and Persistence
The file persists exact model request state, including system instruction text, tool schema, thinking level `HIGH`, and conversation history. It is a golden fixture, not runtime storage. Its important state signal is the distinction between a JSON null value and argument conversion semantics.

## Dependencies and Integration Points
It integrates with `google.golang.org/genai`, aflow schema generation, text/template rendering for tool placeholders, and `convertFromMap` argument conversion. The matching trajectory file records the execution-side error.

## Risks
Nullable pointer arguments are easy to regress: a schema may allow null while the converter treats null as missing. This fixture captures that current behavior. Any intentional fix for nil pointer handling must update both request and trajectory goldens.

## Test Signals
The test signal is the exact two-request history and the error response `missing argument "Optional"` after a null tool call.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/testdata/TestNilToolArg.llm.json -->
