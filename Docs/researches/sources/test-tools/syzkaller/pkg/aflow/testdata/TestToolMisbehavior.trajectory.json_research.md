# sources/test-tools/syzkaller/pkg/aflow/testdata/TestToolMisbehavior.trajectory.json

## Purpose
Golden trajectory fixture for an aflow test where an LLM agent misuses tools before eventually completing. It records the expected span stream for a `test` flow, a `smarty` agent, repeated LLM turns, tool invocations, typed tool-call errors, and the final set-results path.

## Important Data and APIs
The file is JSON data consumed by aflow tests rather than executable code. Its schema matches `trajectory.Span`: `Seq`, `Nesting`, `Type`, `Name`, timestamps, tool `Args`, `Results`, `Error`, agent `Instruction`/`Prompt`/`Reply`, and LLM metadata. It contains flow, agent, llm, and tool spans.

## Control Flow
The fixture models start/finish span pairs in sequence. The agent starts, an LLM turn emits tool calls, successful and failing tools execute, more LLM turns follow after runtime feedback, and the workflow finishes with agent and flow result spans.

## State and Persistence Behavior
It is persisted testdata for deterministic comparison. State is represented only as serialized event history; there are no mutable runtime side effects.

## Dependencies and Integration Points
Integrated by aflow workflow tests and trajectory serialization logic. It also exercises HTML/console consumers that expect stable `SpanType` strings.

## Risks and Test Signals
Risk is fixture drift when span serialization, error wording, or tool validation changes. Strong test signal is exact JSON comparison because it catches ordering, nesting, and bad-call error regressions.
