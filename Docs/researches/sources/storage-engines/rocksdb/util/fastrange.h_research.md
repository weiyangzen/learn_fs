# sources/storage-engines/rocksdb/util/fastrange.h

Purpose: fast alternative to modulo for mapping uniformly distributed 32-bit or 64-bit hashes into a range.

Important APIs/types: `FastRangeGeneric<Hash, Range>()` delegates to specialized `FastRangeGenericImpl`. `FastRange32(uint32_t, uint32_t)` and `FastRange64(uint64_t, size_t)` are the recommended wrappers.

Control flow: 32-bit mapping multiplies `range * hash` into 64 bits and returns the high 32 bits. 64-bit mapping uses `__uint128_t` when available or a decomposed 64x64-to-high64 multiplication fallback.

State and persistence: no state. Results are deterministic but depend on input hash width; this matters for in-memory layout and probabilistic structures, not persisted formats here.

Dependencies and integration: includes type traits and namespace. Used by DynamicBloom, filter benchmarks, hash helpers, and any code mapping hash values to buckets.

Risks: using `FastRange64` on a 32-bit-quality hash can produce very poor distribution, often near zero; comments warn the templated form can hide this mistake. Range type must be unsigned and no wider than hash type.

Test signals: no direct test in this subset, but DynamicBloom/filter benchmark exercise practical use.
