# sources/object-store/rustfs/crates/utils/src/hash.rs

Purpose: Hashing utilities for bitrot protection, bucket distribution, and compatibility.

Important APIs/state: `HashAlgorithm` enum (`SHA256`, `HighwayHash256`, default `HighwayHash256S`, legacy streaming HighwayHash key, `BLAKE2b512`, `Md5`, `None`), private `HashEncoded` storage, `hash_encode`, `size`, `EMPTY_STRING_SHA256_HASH`, `DEFAULT_SIP_HASH_KEY`, `sip_hash`, and `crc_hash`.

Control flow: `hash_encode` dispatches to the chosen algorithm, returning fixed-size stack arrays behind an `AsRef<[u8]>` enum. HighwayHash variants use fixed 32-byte keys converted into four `u64`s; legacy mode preserves main-branch compatibility. `sip_hash` and `crc_hash` hash string keys then mod by cardinality.

State and dependencies: Stateless. Depends on `sha2`, `blake2`, `md-5`, `highway`, `siphasher`, `crc-fast`, `serde`, and `hex-simd` in tests.

Integration points: Enabled by utils `hash` feature; likely used by object storage bitrot and sharding logic.

Risks and tests: `sip_hash`/`crc_hash` divide by `cardinality`, so zero cardinality will panic. MD5 is included and should only be used where non-cryptographic compatibility is acceptable. Tests cover output sizes, deterministic/different hashes, bitrot self-test vectors, and HighwayHash compatibility data.
