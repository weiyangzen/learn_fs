# sources/storage-engines/tikv/src/coprocessor/statistics/fmsketch.rs

Purpose: implements TiDB-compatible Flajolet-Martin sketch for approximate NDV estimation during analyze.

Important APIs/types: `FmSketch::new(max_size)` creates a sketch with mask level zero and a hash set sized to `max_size + 1`. `insert` hashes input bytes with Murmur3 and delegates to `insert_hash_value`. `insert_hash_value` skips hashes filtered by the current mask, inserts retained hashes, and when the set exceeds `max_size`, advances the mask and prunes hashes not matching the new trailing-zero level. `From<FmSketch> for tipb::FmSketch` serializes the mask and hash set.

State and persistence: in-memory mask and hash set are request-local, then serialized in analyze responses. Dependencies are `collections::HashSet`, `mur3`, and `tipb`.

Integration points: column, row sampling, column-group, index, and common-handle analyze paths use FM sketches to estimate distinct values. Risks include poor behavior with extremely small `max_size`, sensitivity to hash compatibility with TiDB, and memory usage proportional to the configured sketch size. Tests port TiDB expectations for NDV estimates over generated data and verify pruning when `max_size` is two.
