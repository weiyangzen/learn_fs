# sources/sync-backup/kopia/repo/content/index/index_v1.go

Final split target: `Docs/researches/sources/sync-backup/kopia/repo/content/index/index_v1.go_research.md`.

Purpose: implements version 1 binary pack indexes, the older format without per-content compression or encryption-key metadata.

Important APIs and types: `Version1`, `FormatV1`, `indexV1`, `indexBuilderV1`, `buildV1`, `v1ReadHeader`, and `openV1PackIndex`. Reader methods implement `ApproximateCount`, `GetInfo`, `Iterate`, and `Close`. Entries store key bytes and a fixed 20-byte value containing timestamp, format version, pack blob name offset/length, delete flag plus pack offset, and packed length.

Control flow: readers binary-search sorted keys with `findEntryPosition` or `findEntryPositionExact`, decode entries through `entryToInfoStruct`, and lazily resolve pack blob IDs from extra data with a mutex-backed offset cache. Builders prepare extra pack-name data, enforce a single key length, reject compression and encryption key IDs, write the header, sorted entries, and extra data.

State and persistence behavior: v1 does not persist original length, so readers compute `OriginalLength = PackedLength - encryptor overhead`. Deleted entries still require a pack blob ID in the serialized record.

Dependencies: `blob.ID`, big-endian helpers, `safeSlice`, sorting, buffering, and errors.

Risks and tests: v1 limitations are compatibility-sensitive. Compression must be rejected before writing. Pack index tests validate v1 round trips, original-length reconstruction, lookup, iteration, random suffix stability, and fuzzed corrupted indexes.
