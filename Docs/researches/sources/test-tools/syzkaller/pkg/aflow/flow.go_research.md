# sources/test-tools/syzkaller/pkg/aflow/flow.go

## Purpose

`flow.go` defines aflow's workflow registry and typed dataflow contract. It binds workflow input/output schemas to concrete action graphs and verifies those graphs at registration time.

## Important APIs, Types, and Functions

`Flow` contains name, consts, root action, model list, and `FlowType`. `FlowType` stores the stable `ai.WorkflowType`, description, input checker, and output extractor. `Flows` is the global registry. Public `Register[Inputs, Outputs]` delegates to `register`, which builds a `FlowType` and calls `registerOne`.

## Control Flow

Registration creates conversion functions for `Inputs` and `Outputs`. Each flow name is normalized to the workflow type string for the main implementation or `type-name` for secondary implementations. `registerOne` rejects duplicate names, creates a verification context, provides consts and inputs, verifies the root action graph, requires all output fields, finalizes unused/missing checks, collects used model names, and inserts the flow.

## State and Persistence Behavior

The global `Flows` map persists registered flows for the process lifetime. Flow consts are copied into execution state on every run by `Execute`.

## Dependencies and Integration Points

It depends on `ai.WorkflowType` and schema/verification helpers in the aflow package. All concrete flow packages register themselves from `init` functions.

## Risks and Edge Cases

Registration panics through the public `Register`, so broken flow definitions fail during package initialization. Flow names are global. Consts can conflict with inputs or be unused. Model lists are inferred from verification, so tools/agents that fail to verify accurately could affect scheduling/UI metadata.

## Test Signals

Flow tests cover a complex pipeline, no-input errors at execution time, flow consts, and registration errors for const conflicts/unused consts.
