# sources/test-tools/syzkaller/pkg/aflow/testdata/TestWorkflow.trajectory.json

## Purpose
Comprehensive golden trajectory for the aflow workflow exercised by `TestWorkflow.llm.json`.

## Important Data and APIs
The fixture contains `Span` records for flow, function actions, a `smarty` agent, nested LLM/tool spans, `agent-candidates`, `swarm` agents, and an `aggregator` agent. It records arguments, results, thoughts, model names, replies, and closing flow results.

## Control Flow
The workflow runs a function action, invokes the main agent, executes tools, records `set-results`, runs candidate agents as a logical group, aggregates their replies, runs another action, and closes the flow.

## State and Persistence Behavior
Static event history. State flow is visible through action outputs, tool results, agent replies, and final flow result fields.

## Dependencies and Integration Points
Used by aflow workflow tests, trajectory serialization, HTML rendering, and any tooling relying on nesting/sequence invariants.

## Risks and Test Signals
The fixture catches regressions in span pairing, nested candidate representation, model attribution, result propagation, and deterministic ordering of arguments/results.
