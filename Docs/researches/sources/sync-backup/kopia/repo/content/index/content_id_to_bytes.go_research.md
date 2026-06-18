# sources/sync-backup/kopia/repo/content/index/content_id_to_bytes.go

Final split target: `Docs/researches/sources/sync-backup/kopia/repo/content/index/content_id_to_bytes.go_research.md`.

Purpose: provides compact byte conversions used by binary index encoders and decoders. The binary representation stores one prefix byte followed by raw hash bytes.

Important APIs: `bytesToContentID` converts an encoded byte slice into an `ID`, accepting empty input as `EmptyID` and panicking if the slice is longer than the maximum supported ID length plus prefix. `contentIDToBytes` appends prefix plus hash bytes to a caller-provided output buffer. `contentIDBytesGreaterOrEqual` wraps bytewise comparison for binary searches.

Control flow, State and persistence: these helpers are pure except for the explicit panic on impossible oversized encoded IDs. They do not validate that the prefix is semantically valid; callers are index readers working from trusted or separately bounds-checked binary data.

Dependencies and integration: used by v1/v2 index builders and readers for sorted entry keys and exact/range search. The ordering must remain consistent with `ID.less` and string-like prefix ordering for merged iteration and range scans.

Risks and tests: an ordering mismatch would break binary search, `PrefixRange`, and merged index iteration. `packindex_internal_test.go` verifies round trips for empty, unprefixed, and prefixed IDs; broader pack index tests validate lookup and iteration over encoded keys.
