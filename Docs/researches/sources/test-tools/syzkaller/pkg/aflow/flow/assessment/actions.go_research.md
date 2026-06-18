# sources/test-tools/syzkaller/pkg/aflow/flow/assessment/actions.go

## Purpose

`actions.go` contains a small shared assessment action that normalizes LLM explanations for email/dashboard presentation.

## Important APIs, Types, and Functions

`formatExplanation = aflow.NewFuncAction("format-explanation", formatExplanationFunc)`. `formatExplanationArgs.ExplanationRaw` is the input and `formatExplanationResult.Explanation` is the output. `formatExplanationFunc` calls `email.WordWrap` at 80 columns.

## Control Flow

The action is a direct transformation: read raw explanation from workflow state, word-wrap it, and emit `Explanation`.

## State and Persistence Behavior

It is stateless and does not use cache, filesystem, or external services. The output becomes a persisted dashboard workflow field through assessment output structs.

## Dependencies and Integration Points

It depends on aflow action wrapping and `pkg/email` word wrapping. KCSAN, moderation, and security assessment flows use it after their LLM agent.

## Risks and Edge Cases

Wrapping may affect markdown/code formatting if the LLM emits structured text. The fixed 80-column width is chosen for readability but may not match all UI contexts.

## Test Signals

No direct unit test is present. It is indirectly verified by flow registration because it consumes `ExplanationRaw` and produces required `Explanation`.
