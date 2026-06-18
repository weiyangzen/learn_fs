# sources/object-store/rustfs/crates/ecstore/src/bucket/lifecycle/rule.rs

## Purpose

This file implements lifecycle rule filter helpers for tag and object-size matching, plus minimal transition validation. It is used by `core.rs` when deciding whether a lifecycle rule applies to an object or multipart upload candidate.

## Important APIs, Types, and Functions

- `Filter` trait defines `test_tags(&self, user_tags: &str) -> bool` and `by_size(&self, sz: i64) -> bool`.
- `impl Filter for LifecycleRuleFilter` decodes object tags and checks single-tag, AND-tag, top-level size, and AND-size constraints.
- `requires_tag_matching` returns whether the filter has any tag constraints.
- `tag_matches` requires both tag key and value to be present and equal to decoded user tags.
- `and_tags_match` requires all tags in the AND operator to match.
- `and_size_matches` applies AND-scoped greater-than and less-than size constraints.
- `TransitionOps` trait defines `validate`.
- `impl TransitionOps for Transition` rejects transitions that specify both `Date` and positive `Days`, and rejects missing storage class.

## Control Flow

`test_tags` returns true immediately when a lifecycle filter has no tag constraints. When tag constraints exist, it decodes the URL-encoded S3 tag string through `decode_tags_to_map`, then requires both the top-level `Tag` and every `And.Tags` entry to match when present.

`by_size` clamps negative object sizes to zero, then applies top-level `ObjectSizeGreaterThan` and `ObjectSizeLessThan`, followed by any AND-scoped size constraints. Bounds are strict: size must be greater than the minimum and less than the maximum.

`TransitionOps::validate` enforces that a transition has exactly one timing mode in practice for date/positive-days conflicts and that a storage class exists.

## State and Persistence Behavior

The file is stateless and performs no persistence. It transforms provided filter DTOs and tag strings into boolean decisions used by lifecycle evaluation.

## Dependencies and Integration Points

It depends on `crate::bucket::tagging::decode_tags_to_map` and `s3s::dto::{LifecycleRuleAndOperator, LifecycleRuleFilter, Tag, Transition}`.

`core.rs` calls:

- `<LifecycleRuleFilter as Filter>::test_tags(filter, &obj.user_tags)` during rule filtering.
- `<LifecycleRuleFilter as Filter>::by_size(filter, obj.size as i64)` for non-delete-marker object filtering.

Stale multipart cleanup in `bucket_lifecycle_ops.rs` constructs `ObjectOpts` with object name, user tags, size, and initiation time; those options flow through `core.rs` and this filter logic for abort-incomplete rules.

## Risks and Edge Cases

- `TransitionOps::validate` allows `date` plus `days == 0`; the error text says exactly one of Days or Date should be present, but the implementation only rejects date plus positive days.
- `test_tags` relies on `decode_tags_to_map`; malformed tag strings may decode to an empty or partial map depending on that helper.
- Missing tag key or value always fails that specific tag match.
- Size bounds are strict, matching S3 lifecycle filter semantics, so boundary equality does not match.
- Negative sizes are clamped to zero, avoiding accidental lower-bound matches for invalid size inputs.

## Test Signals

Local unit tests cover single-tag matching, all-tags matching for AND filters, strict object-size bounds, and the fact that filters without tag constraints accept any tag string. There are no local tests for transition validation, malformed tag decoding, combined top-level and AND size constraints, or date plus zero-day transition behavior.
