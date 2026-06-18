# sources/sync-backup/kopia/repo/content/index/index_v2.go

Final split target: `Docs/researches/sources/sync-backup/kopia/repo/content/index/index_v2.go_research.md`.

Purpose: implements version 2 binary pack indexes, adding per-content compression metadata, format version, encryption key ID, compact pack ID tables, and larger optional length fields.

Important APIs and types: `Version2`, `FormatV2`, `indexV2`, `indexBuilderV2`, `indexV2FormatInfo`, `buildV2`, `newIndexBuilderV2`, `openV2PackIndex`, and parsing/writing helpers. Entries contain relative timestamp, pack offset plus deleted flag, 24-bit original and packed lengths, pack index, optional format index, optional extended pack index, and optional high length bits.

Control flow: builder analysis chooses entry size based on number of unique formats, pack count, and maximum lengths. It rejects too many formats, too many packs, content lengths at or above 28 bits, and pack offsets at or above 1 GiB. It writes sorted entries, pack side table, format side table, and pack-name extra data. Readers parse header, pre-read format and pack tables, binary-search keys, and decode entries back to `Info`.

State and persistence behavior: v2 persists enough metadata for compressed content and multiple format/encryption variants. `baseTimestamp` is present in the format but this source leaves it at zero during builds.

Dependencies: blob IDs, compression header IDs, big-endian helpers, safe slicing, sorting, and errors.

Risks and tests: compact fields create boundary risks for lengths, offsets, pack counts, and format IDs. Tests cover v2 round trips, per-content limits, too many formats, corrupted-byte fuzzing, sorting, and sharding.
