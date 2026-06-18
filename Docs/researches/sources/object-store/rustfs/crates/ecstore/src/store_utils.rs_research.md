# sources/object-store/rustfs/crates/ecstore/src/store_utils.rs

## Purpose

Provides ECStore metadata cleanup and bucket-name validation helpers.

## Important APIs and Types

`clean_metadata`, `remove_standard_storage_class`, and `clean_metadata_keys` mutate metadata maps. `is_reserved_or_invalid_bucket` exposes bucket filtering. Private helpers check RustFS metadata buckets, the reserved name `rustfs`, IP-shaped names, strict lowercase S3-style names, and non-strict names allowing uppercase, underscores, and colons.

## Control Flow

Metadata cleanup removes standard storage class and generated headers. Bucket validation trims a trailing slash, checks empty/length/IP shape, applies strict or non-strict regex, rejects `..`, `.-`, and `-.`, then rejects metadata/reserved buckets.

## State and Persistence Behavior

Only caller-owned `HashMap` values are mutated. Regexes are compiled once with `LazyLock`; no durable state is written.

## Dependencies and Integration Points

Uses storage-class constants, metadata bucket constants, and HTTP header constants. Listing uses bucket validation to mark reserved/invalid listings transient.

## Risks and Edge Cases

The public boolean conflates reserved and invalid reasons. Non-strict mode intentionally accepts names strict S3 rejects. Header removal is exact-key based. The IP regex checks only dotted shape, not octet ranges.

## Test Signals

Tests cover invalid and valid bucket names, strict/non-strict differences, reserved buckets, trailing slash stripping, and repeated regex-backed calls.
