# sources/test-tools/syzkaller/pkg/aflow/trajectory/trajectory.go

## Purpose
Defines aflow execution span data and console string formatting for trajectory logging.

## Important APIs, Types, and Functions
`Span` records sequence, nesting, type, name, model, timestamps, errors, args/results, agent instruction/prompt/reply, LLM thoughts, and token counts. `SpanType` constants define stable string values. `(*Span).String` formats start/finish logs, and `printMap` deterministically prints sorted map keys.

## Control Flow
`String` branches on whether `Finished` is zero and on span type. Start spans print prompts or tool args where relevant. Finished spans print results, replies, LLM tokens/thoughts/replies, or tool results. Unknown span types panic.

## State and Persistence Behavior
`Span` is a serializable record persisted in trajectory JSON and dashboard data. The code itself stores no global state.

## Dependencies and Integration Points
Used throughout aflow for workflow tracing, test fixtures, dashboards, and HTML rendering.

## Risks and Test Signals
Stable `SpanType` strings are database-facing and should not change casually. Map sorting avoids nondeterministic logs. Golden trajectory fixtures are the main regression signal.
