# sources/test-tools/syzkaller/pkg/aflow/flow/patching/iteration.go

## Purpose

`iteration.go` registers the patch-iteration workflow that processes reviewer feedback, updates tags, decides whether to produce a new patch version, regenerates code/description/fixes metadata when needed, and drafts direct replies.

## Important APIs, Types, and Functions

`PatchIterationInputs` describes environment, bug context, patch history, base tags, base commit selection, and strace fields. Structured outputs include `verdictAgentOutputs` and `changelogGeneratorOutputs`, with validators `validateVerdictOutputs` and `validateChangelogOutputs`. Helper tools/actions include `viewPatchHistoryTool`, `extractTriageResults`, `extractNewComments`, `extractLatestPatchInfo`, `resolveFixes`, and `appendCommentReply`.

## Control Flow

The registered workflow prepares the base kernel, reproduces the bug, indexes code, extracts new/latest patch-history state, asks a verdict agent to categorize feedback into code/description/fixes/resend needs, extracts and merges review tags, computes whether a new version is needed, and conditionally enters a patch update branch. In that branch it creates a scratch tree, applies the previous patch, runs code generation only when `CodeItems` exist or forwards the old diff otherwise, optionally refreshes the Fixes tag, resolves final Fixes metadata, gathers recent commits, generates changelog/description, and gets maintainers. Finally it iterates over `NewComments` to decide and append direct comment replies.

## State and Persistence Behavior

State is accumulated in the aflow execution map, including persistent semantic fields such as `NeedNewVersion`, `PatchDiff`, tags, `NewChangeLog`, and `Replies`. Scratch source mutations happen only inside the conditional branch and are reset by `crash.TestPatch`. No new cache is used directly here beyond actions in the pipeline.

## Dependencies and Integration Points

It integrates patching helpers, kernel actions, crash reproduction, code search, `aflow.If`, `aflow.ForEach`, LLM structured outputs, common code tools, and email word wrapping. It produces `ai.PatchIterationOutputs`.

## Risks and Edge Cases

Patch history must be non-empty; helper actions return flow errors otherwise. Prompt-injection risk from external comments is mitigated by JSON-encoding comments and explicit instructions, but LLM compliance remains critical. `NeedNewVersion` is true even for resend-only requests. If only description changes are requested, the old patch is applied and forwarded without code generation. Reply generation trusts LLM-provided `Action` strings and only appends when exactly `reply` with non-empty text.

## Test Signals

No dedicated tests cover the whole workflow. Registration tests validate dataflow. Validators are small and deterministic but currently not separately tested in the assigned files.
