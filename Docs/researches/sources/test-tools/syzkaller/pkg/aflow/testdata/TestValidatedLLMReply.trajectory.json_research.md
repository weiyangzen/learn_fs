# sources/test-tools/syzkaller/pkg/aflow/testdata/TestValidatedLLMReply.trajectory.json

## Purpose
Golden trajectory for a plain reply validation scenario where the first LLM reply fails validation and the final agent reply is changed.

## Important Data and APIs
The file serializes `trajectory.Span` records for flow, agent, and two LLM attempts. The closing agent span contains `Reply: changed-reply`; the closing flow span stores `Results.Result` with the same value.

## Control Flow
The agent starts, performs one LLM call, performs a second retry LLM call after validation failure, then returns the corrected reply through flow results.

## State and Persistence Behavior
Immutable fixture state only. It records retry chronology and final accepted reply.

## Dependencies and Integration Points
Used by aflow validation tests and trajectory renderers. It validates that reply-level verification does not require tool spans.

## Risks and Test Signals
Potential regressions include missing retry spans, wrong final reply propagation, or changed nesting. Exact JSON comparison is the primary signal.
