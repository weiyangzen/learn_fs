# sources/object-store/rustfs/crates/config/src/constants/compress.rs

## Purpose
Defines HTTP response compression configuration constants, defaulting compression off to align with MinIO behavior.

## Important APIs, types, and functions
Exports env names and defaults for compression enablement, extension allowlist, MIME type allowlist, and minimum compressed size. Defaults are disabled, empty extension list, MIME types `text/*,application/json,application/xml,application/javascript`, and 1000 byte minimum size.

## Control flow
No executable flow; HTTP response code reads these constants through configuration parsing.

## State and persistence behavior
Static constants only.

## Dependencies and integration points
Integrated by server HTTP middleware or response writers that decide whether to compress content by env configuration, file extension, MIME type, and size.

## Risks and edge cases
Compression is security/performance-sensitive; enabling it for authenticated or secret-adjacent responses can expose side channels if not considered by higher layers. Wildcard MIME matching and extension normalization must be implemented downstream. Static defaults cannot express per-bucket or per-route policy.

## Test signals
No local tests; compression parser and HTTP response tests should verify accepted boolean values, MIME wildcard matching, extension handling, min-size enforcement, and disabled default.
