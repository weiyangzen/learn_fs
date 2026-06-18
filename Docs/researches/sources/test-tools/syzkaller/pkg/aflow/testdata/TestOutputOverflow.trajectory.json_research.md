<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/testdata/TestOutputOverflow.trajectory.json -->
# Research: sources/test-tools/syzkaller/pkg/aflow/testdata/TestOutputOverflow.trajectory.json

## Purpose
This trajectory is the execution golden for `TestOutputOverflow`. It verifies that output overflow is surfaced as span errors while the agent can still accept structured results before a later terminal overflow.

## Important APIs, Types, and Functions
It records `LLMAgent` spans, LLM spans with error values, and the `set-results` tool span. Relevant implementation areas are `parseLLMError` style response handling, finish-reason processing, and agent retry control.

## Control Flow
The file has 10 spans: 2 flow, 2 agent, 4 LLM, and 2 tool spans. Three initial LLM attempts finish with `MAX_TOKENS`, then the model calls `set-results` and the tool records `Output: 42`. A later invocation again overflows enough for the overall final expected error value to be `MAX_TOKENS`.

## State and Persistence
The trajectory persists `Output: 42` as an intermediate result and `MAX_TOKENS` errors on LLM spans. It protects the distinction between recoverable overflow attempts and final failure behavior.

## Dependencies and Integration Points
It is paired with `TestOutputOverflow.llm.json` and depends on genai finish reason string serialization. It also integrates with final result comparison in the test harness, where the expected test output is the max-token error string.

## Risks
Changing overflow span recording, retry limits, or set-results retention could make the trajectory misleading. The main behavioral risk is either losing successful structured output after retries or masking a final overflow as success.

## Test Signals
Expected signals are three recorded `MAX_TOKENS` errors, one `set-results` tool result `Output: 42`, and a final agent/flow error path matching `MAX_TOKENS`.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/testdata/TestOutputOverflow.trajectory.json -->
