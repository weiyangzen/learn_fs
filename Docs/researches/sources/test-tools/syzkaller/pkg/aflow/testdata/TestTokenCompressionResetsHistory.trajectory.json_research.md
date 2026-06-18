<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/testdata/TestTokenCompressionResetsHistory.trajectory.json -->
# Research: sources/test-tools/syzkaller/pkg/aflow/testdata/TestTokenCompressionResetsHistory.trajectory.json

## Purpose
This trajectory is the execution golden for `TestTokenCompressionResetsHistory`. It proves that compression resets duplicate tool-call history while preserving agent progress.

## Important APIs, Types, and Functions
It records `LLMAgent` spans, compressor LLM span `smarty-compressor`, and repeated `tick` tool spans. The most important implementation state is `agentSession.toolHistory`, which must be cleared when context is compressed.

## Control Flow
The file has 24 spans: 2 flow, 2 agent, 12 LLM, and 8 tool spans. Four `tick` executions return `ResFoo: 123`. Compression occurs after the third tick and records reply `compressed summary`; the fourth identical tick is then allowed and the agent returns `Done`.

## State and Persistence
The fixture persists all four successful tool results and final `Reply: Done`. It guards against loop-detection state leaking across compression.

## Dependencies and Integration Points
It pairs with the request fixture and depends on both genai usage metadata and trajectory span naming. It also integrates with `defaultLoopDetectionLimit`, where repeated identical calls are otherwise bounded.

## Risks
The main risk is false-positive loop detection after compression. A secondary risk is clearing too much state, such as losing accepted tool results needed in the summary.

## Test Signals
Expected signals are four `tick` tool results, one compressor reply `compressed summary`, no duplicate-call error, and final flow result `{"Reply":"Done"}`.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/aflow/testdata/TestTokenCompressionResetsHistory.trajectory.json -->
