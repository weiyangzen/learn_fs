# sources/sync-backup/kopia/repo/content/index/packindex_test.go

Final split target: `Docs/researches/sources/sync-backup/kopia/repo/content/index/packindex_test.go_research.md`.

Purpose: broad regression suite for pack index builders, binary encoders/decoders, sorting, sharding, and corrupted-input tolerance.

Important fixtures: deterministic helpers generate content IDs with mixed prefixes, pack blob IDs, offsets, original and packed lengths, format versions, compression IDs, encryption key IDs, and timestamps. `fakeEncryptionOverhead` models v1 original-length reconstruction.

Control-flow coverage: `TestPackIndex_V1` and `TestPackIndex_V2` build indexes through multiple paths, compare stable prefixes, require random suffix differences, open indexes, verify `GetInfo`, full iteration, prefix iteration, missing lookups, and fuzzed mutations. Limit tests validate v2 content length and pack offset boundaries. Sorting tests cover regular and one-use builders. Unique-format tests enforce the v2 255-format cap. Shard tests verify deterministic shard counts, lengths, and full ID coverage for both builders.

State and persistence behavior: tests confirm that serialized bytes are stable except for random uniqueness suffixes and that one-use builders drain on sharding. V1 field loss is explicitly normalized by replacing original length with packed length minus overhead.

Dependencies: `testify/require`, random data, SHA1 deterministic IDs, compression headers, blob IDs, and index internals.

Risks and gaps: fuzzing is mutation-based and not property-guided, but it meaningfully asserts corrupted index input should not panic when opened and partially iterated.
