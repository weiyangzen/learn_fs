# sources/storage-engines/tikv/src/coprocessor/statistics/cmsketch.rs

Purpose: implements Count-Min Sketch for approximate point-query frequency estimates, plus TopN extraction support for analyze V2.

Important APIs/types: `CmSketch::new(depth, width)` returns `None` if either dimension is zero. `insert` hashes bytes with Murmur3 x64 128-bit and increments one counter per row using double hashing. `sub` removes counts from the sketch with saturating row subtraction and decrements total count. `push_to_top_n` records exact heavy-hitter entries. `From<CmSketch> for tipb::CmSketch` serializes rows and TopN entries.

State and persistence: the sketch holds in-memory counter rows, total count, and TopN data; it is serialized into analyze responses but not persisted directly by TiKV. Dependencies are `mur3`, `tipb`, and test-only datatype/zipf helpers.

Integration points: `SampleCollector` and index analyze paths insert encoded column/index values; analyze V2 subtracts TopN values from the CM sketch and stores them separately. Risks include `sub` using `self.count -= cnt` without saturating the total, parameter zero disabling the sketch, and estimator compatibility with TiDB's expected encoding. Tests verify deterministic Murmur hashes and average error on Zipf-distributed encoded values.
