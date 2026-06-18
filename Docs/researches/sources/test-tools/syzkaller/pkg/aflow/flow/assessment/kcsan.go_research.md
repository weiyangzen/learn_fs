# sources/test-tools/syzkaller/pkg/aflow/flow/assessment/kcsan.go

## Purpose

`kcsan.go` registers the KCSAN assessment workflow, which determines whether a reported data race is benign and only needs annotations.

## Important APIs, Types, and Functions

`kcsanInputs` describes target, crash report, kernel repo/commit/config fields. `kcsanPrompt` embeds the crash report. The package `init` registers `ai.WorkflowAssessmentKCSAN` with output type `ai.AssessmentKCSANOutputs`.

## Control Flow

The workflow checks out and builds the kernel, prepares a code-search index, runs an `LLMAgent` named `expert` with the embedded KCSAN instruction prompt and `common.CodeAccessTools`, requests a structured `Benign` bool plus raw textual explanation, then runs `formatExplanation`.

## State and Persistence Behavior

Kernel checkout and build artifacts are cached by their actions. The LLM result and formatted output are stored in aflow state and later extracted into persisted dashboard output fields.

## Dependencies and Integration Points

It integrates kernel actions, `codesearcher.PrepareIndex`, common prompt loading, and code access tools. The prompt content is embedded by `prompts.go`.

## Risks and Edge Cases

The assessment relies on LLM use of actual code access tools; misleading reports or missing code index/build failures can affect output. The workflow always builds before assessment, so build failures block moderation-style classification.

## Test Signals

Global flow registration tests load this package and verify required dataflow. There are no semantic tests for KCSAN classifications.
