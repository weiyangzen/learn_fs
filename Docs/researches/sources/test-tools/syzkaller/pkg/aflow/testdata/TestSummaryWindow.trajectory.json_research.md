<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/testdata/TestSummaryWindow.trajectory.json -->
# Research: sources/test-tools/syzkaller/pkg/aflow/testdata/TestSummaryWindow.trajectory.json

## Purpose
This trajectory is the execution golden for `TestSummaryWindow`. It verifies that sliding-window summarization preserves forward progress across many tool calls and ends with reply `Done`.

## Important APIs, Types, and Functions
It records `LLMAgent` LLM spans and `tick` tool spans. The key implementation state is `agentSession.req` plus `summaryMessage`, with `summaryWindow` deciding when to ask for model summary text.

## Control Flow
The file has 34 spans: 2 flow, 2 agent, 16 LLM, and 14 tool spans. Seven `tick` tool executions return `ResFoo: 123`. The model eventually stops calling tools and returns text `Done`.

## State and Persistence
The trajectory persists repeated tool outputs and final flow result `{"Reply":"Done"}`. It does not show every trimmed request message directly; that role belongs to the `.llm.json` fixture. Together they protect both runtime spans and request history.

## Dependencies and Integration Points
It pairs with `TestSummaryWindow.llm.json` and depends on deterministic fake time and span sequencing. It also integrates with tool result serialization and final reply extraction.

## Risks
If summary-window trimming breaks tool history or summary insertion, the agent may loop, lose context, or fail to finish. Span counts and final reply provide broad regression coverage.

## Test Signals
Expected signals are 7 successful `tick` results, no errors, and final reply/result `Done`.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/testdata/TestSummaryWindow.trajectory.json -->
