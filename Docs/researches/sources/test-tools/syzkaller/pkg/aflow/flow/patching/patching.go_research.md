# sources/test-tools/syzkaller/pkg/aflow/flow/patching/patching.go

## Purpose

`patching.go` registers the main patch generation workflow. It reproduces a bug, investigates root cause, edits a scratch kernel tree with LLM assistance, tests the patch in a loop, finds Fixes metadata, selects recipients, and generates a commit description.

## Important APIs, Types, and Functions

`Inputs` describes bug, kernel, VM, syzkaller, base branch/commit, and strace settings. `patchGenerationLoop` constructs a `DoWhile` loop around a patch-generating `LLMAgent` and `crash.TestPatch`. Prompt constants define debugger, patch, description, and shared fault-injection/description instructions. Fixes helpers include `fixesFinderState`, `fixesFinderArgs`, `validateFixesHashes`, `formatFixes`, and `queryFixesTag`.

## Control Flow

The workflow picks a base commit, creates a simplified C repro, checks out/builds the kernel, verifies the crash reproduces, prepares code search, asks a debugger agent for root-cause explanation, creates a scratch checkout, runs the patch generation/test loop until `TestError` clears or max iterations is reached, asks a fixes-finder agent for the introducing commit, formats the Fixes tag, gets maintainers and recent commit subjects, and asks a description generator for a wrapped commit message.

## State and Persistence Behavior

Kernel checkouts/builds and repro results are cached by underlying actions. The scratch checkout is mutable and temporary. `patchGenerationLoop` repeatedly updates `PatchExplanation`, `PatchDiff`, and `TestError` in state. Final outputs match `ai.PatchingOutputs`, including tags initialized from const empty slices.

## Dependencies and Integration Points

It integrates actions from `actionsyzlang`, `crash`, `kernel`, tools `codeeditor`, `codesearcher`, `patchdiff`, common code access tools, email wrapping, and `vcs` commit lookup. It is one of the dashboard-facing automated patch workflows.

## Risks and Edge Cases

The workflow trusts LLMs for code edits, root-cause diagnosis, Fixes selection, and description text but validates some outputs. `validateFixesHashes` ensures the hash exists and is reachable from the current commit. Patch loop max iterations bounds runaway repair attempts. Prompt text includes many kernel-process constraints, but code quality still depends on generated edits and VM test fidelity. `TestPatch` cache-key limitations can affect repeated loop behavior.

## Test Signals

Registration tests verify dataflow. `tags_test.go` covers related tag helpers and `actions_test.go` covers recent commits. Full patch generation requires integration with Linux build, VM repro, and LLM stubs.
