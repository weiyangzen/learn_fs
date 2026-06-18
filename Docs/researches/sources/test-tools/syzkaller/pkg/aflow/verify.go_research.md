# sources/test-tools/syzkaller/pkg/aflow/verify.go

## Purpose
Implements static verification helpers for aflow action graphs, checking variable wiring, output usage, model names, and schema validity.

## Important APIs, Types, and Functions
`verifyContext` tracks input/output verification modes, variable state, registered models, and first error. `varState` records producing action, type, and use. Helpers include `newVerifyContext`, `requireInput`, `provideOutput`, `finalize`, `noteError`, `requireInputs`, `provideOutputs`, `provideOutputsMap`, `provideArrayOutputs`, and `requireSchema`.

## Control Flow
Actions call require/provide helpers while a flow is verified. Missing inputs, type mismatches, duplicate outputs, empty required values, invalid schemas, and unused outputs are accumulated through first-error preservation. `finalize` flags any output never consumed.

## State and Persistence Behavior
Verification state is in-memory for one verification pass. No persistence.

## Dependencies and Integration Points
Depends on reflection plus local helpers `foreachFieldOf` and `schemaFor`. Integrated into aflow flow/action/tool definitions before execution.

## Risks and Test Signals
Risks include reflect type equality surprises, map output nil types, and unused-output false positives for intentionally terminal values. Covered indirectly by aflow workflow tests and fixture generation.
