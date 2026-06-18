<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/testdata/TestTokenCompression.trajectory.json -->
# Research: sources/test-tools/syzkaller/pkg/aflow/testdata/TestTokenCompression.trajectory.json

## Purpose
This trajectory is the execution golden for `TestTokenCompression`. It proves that context compression is recorded as an LLM span and the main agent continues to final reply `Done`.

## Important APIs, Types, and Functions
It records spans for agent `smarty`, compressor LLM name `smarty-compressor`, and `tick` tool executions. The relevant state is token accounting from `GenerateContentResponse.UsageMetadata` and the compressed summary reply.

## Control Flow
The file has 16 spans: 2 flow, 2 agent, 8 LLM, and 4 tool spans. Two `tick` calls occur, token growth triggers a compressor LLM span with reply `compressed summary`, and the main agent resumes and returns `Done`.

## State and Persistence
The fixture persists `ResFoo: 123` tool results, compressor reply text, and final flow result `{"Reply":"Done"}`. It protects the execution trace around the request-history truncation captured in the `.llm.json` file.

## Dependencies and Integration Points
It pairs with the LLM request fixture and depends on genai usage metadata being interpreted consistently. It also integrates with trajectory naming for compressor spans.

## Risks
If compression is not recorded, if the compressor reply is treated as the final answer, or if the main request cannot resume from summary, this trajectory will drift or fail.

## Test Signals
Expected signals are the `smarty-compressor` LLM reply `compressed summary`, two successful `tick` tool results, and final reply `Done`.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/testdata/TestTokenCompression.trajectory.json -->
