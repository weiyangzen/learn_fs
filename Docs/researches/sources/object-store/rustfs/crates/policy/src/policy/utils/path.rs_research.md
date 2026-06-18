# sources/object-store/rustfs/crates/policy/src/policy/utils/path.rs

## Purpose

Implements a Rust version of Go's `path.Clean` for slash-separated policy resource matching. It normalizes dot segments, duplicate slashes, trailing slashes, and parent-directory segments.

## Important APIs, Types, and Functions

- `LazyBuf<'a>` delays allocation while building the cleaned path and only allocates when output diverges from input.
- `clean(path: &str) -> String` is the public normalizer.

## Control Flow

`clean` returns `"."` for empty input. It tracks whether the path is rooted, a read index, an output buffer/write index, and a `dotdot` boundary. It skips empty and `.` path elements, collapses `..` by rewinding the output buffer when possible, preserves leading `..` for relative paths, and emits normalized path components separated by single slashes. Empty output becomes `"."`.

## State and Persistence

No persistent state. `LazyBuf` owns temporary output storage for one call.

## Dependencies and Integration Points

Used by `Resource::is_match_with_resolver` before exact/wildcard resource checks. This is a security-sensitive integration because it prevents resource patterns such as `attacker-bucket/*` from matching request paths that normalize outside the bucket.

## Risks and Edge Cases

- Operates on bytes and returns `String::from_utf8_lossy`; if invalid UTF-8 were somehow supplied it would be lossy, though Rust `&str` inputs are valid UTF-8.
- Normalizing object keys may differ from raw S3 object key semantics for keys containing literal `.` or `..` path components. This is intentional for authorization safety but must align with request construction.
- Rooted paths are supported even though S3 resource validation rejects S3 patterns that start with `/`.

## Test Signals

Inline tests mirror many Go path-cleaning cases: empty paths, rooted paths, trailing slashes, duplicate slashes, `.` and `..`, over-parenting, and idempotency of already-clean output.
