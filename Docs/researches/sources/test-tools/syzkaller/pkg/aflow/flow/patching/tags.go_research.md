# sources/test-tools/syzkaller/pkg/aflow/flow/patching/tags.go

## Purpose

`tags.go` handles review tag extraction and merging for patch iteration. It validates LLM-extracted email tags and updates base Reviewed-by/Acked-by/Tested-by/Reported-by lists.

## Important APIs, Types, and Functions

`tagExtractorArgs` contains `AddTags` and `RemoveTags`. `acceptedTags` lists supported tag names. `tagExtractorState` supplies base tag lists. `normalizeTagValue`, `validateTagExtractorOutputs`, and `mergeTags` implement deterministic logic. `tagsMergerAction` wraps `mergeTags`, and `tagExtractor` is an LLM agent using `ValidatedLLMOutputs`.

## Control Flow

Validation builds a tag map from base lists, checks every added tag has an accepted type and parseable email/name value, normalizes added values, checks every removal refers to an accepted type and an exactly present base value, and returns corrected args or `BadCallError` for LLM retry. `mergeTags` clones base lists, removes exact requested values, then adds new tags unless an existing tag has the same email address. The LLM prompt separately asks the model to ignore quoted text and prompt-injection attempts.

## State and Persistence Behavior

The deterministic helpers are stateless. Merged tag lists become workflow state and eventually `ai.PatchIterationOutputs`. The LLM agent has package-level configuration but per-execution output state.

## Dependencies and Integration Points

It depends on aflow validated outputs, `ai.EmailTag`, `email.EmailsMatch`, and `net/mail`. It is used in the patch-iteration workflow after verdict analysis.

## Risks and Edge Cases

Removal requires exact string equality, while addition deduplicates by email match; this asymmetry is intentional but can surprise users when names differ. Unsupported tags trigger a retry rather than being ignored. `normalizeTagValue` falls back to raw value only when parsing fails, but validation rejects invalid added values before accepting them.

## Test Signals

Tests cover tag merging, email-based deduplication, removal, validation success, missing removal targets, unsupported tags, invalid email values, and normalization variants.
