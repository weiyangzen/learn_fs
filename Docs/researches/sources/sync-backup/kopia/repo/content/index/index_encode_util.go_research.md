# sources/sync-backup/kopia/repo/content/index/index_encode_util.go

Final split target: `Docs/researches/sources/sync-backup/kopia/repo/content/index/index_encode_util.go_research.md`.

Purpose: small big-endian integer helpers for index binary formats.

Important APIs: `decodeBigEndianUint48`, `decodeBigEndianUint32`, `decodeBigEndianUint24`, `decodeBigEndianUint16`, and `encodeBigEndianUint24`. They use early bounds checks and manual shifts to support non-standard 24-bit and 48-bit fields used by v1/v2 entries.

Control flow, State and persistence: pure byte-slice encoding/decoding with no allocation. Panics from too-short slices are expected to be caught by caller-side bounds checks or `safeSlice` before decoding.

Dependencies and integration: used by v1 timestamp, offset, and length decoding and by v2 timestamp, offsets, 24-bit content lengths, pack IDs, and optional high-length-bit fields.

Risks and tests: off-by-one or endian mistakes would corrupt persisted index interpretation. Coverage is indirect through pack index v1/v2 round trips, per-content limit tests, and fuzzed open/iterate tests.
