# sources/test-tools/syzkaller/pkg/aflow/flow/patching/tags_test.go

## Purpose

`tags_test.go` verifies deterministic review tag validation, normalization, merge, removal, and deduplication behavior.

## Important APIs, Types, and Functions

`TestMergeTags` calls `mergeTags`. `TestValidateTagExtractorOutputs` calls `validateTagExtractorOutputs`. `TestNormalizeTagValue` calls `normalizeTagValue`.

## Control Flow

The merge test starts with base tags, adds new and duplicate tags, removes one tag, and checks final per-tag slices. Validation table cases cover valid tags and removals, removal of a missing tag, unsupported tag types, and invalid email values. Normalization cases cover quoted names, whitespace, bare email, angle-only email, and invalid fallback.

## State and Persistence Behavior

The tests use an empty `aflow.Context` and do not rely on persistent state. They operate on in-memory slices.

## Dependencies and Integration Points

They use `ai.EmailTag`, aflow error semantics, and `testify/require`. These tests guard the non-LLM parts of patch-iteration tag processing.

## Risks and Edge Cases

The tests do not execute `tagExtractor` LLM prompts, so quoted-text/prompt-injection behavior remains prompt-only. Removal normalization is not applied, so exact removal matching is preserved and tested indirectly.

## Test Signals

The suite provides strong coverage for accepted tag policy and duplicate prevention by email address.
