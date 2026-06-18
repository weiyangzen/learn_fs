# sources/test-tools/syzkaller/pkg/aflow/trajectory/html/trajectory.go

## Purpose
Renders aflow trajectory spans into full HTML reports or reusable trajectory snippets.

## Important APIs, Types, and Functions
Embeds `report.html` and `trajectory_block.html`. `UIAITrajectorySpan` is the view model. `PopulateToolCalls` associates tool names with the next LLM span at the same nesting. `RenderReport`, `RenderTrajectory`, and `marshalJSON` prepare templates and JSON.

## Control Flow
`RenderReport` converts raw `trajectory.Span` records to UI spans, computes durations, marshals args/results, populates tool-call associations, marshals UI spans to JSON, parses templates with shared HTML funcs, and executes. `RenderTrajectory` does the same for only the shared block.

## State and Persistence Behavior
No persistent state; writes rendered HTML to the provided writer or buffer.

## Dependencies and Integration Points
Depends on `trajectory`, syzkaller `pkg/html` template funcs, Go `html/template`, and embedded templates. Consumes golden trajectory fixtures indirectly through tests/reports.

## Risks and Test Signals
Risks include unsafe JSON embedding, template parse failures, and wrong tool attribution across nesting levels. Tests focus on `PopulateToolCalls` nesting behavior.
