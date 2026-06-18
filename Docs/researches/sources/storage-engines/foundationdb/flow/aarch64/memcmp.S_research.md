<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/aarch64/memcmp.S -->
# sources/storage-engines/foundationdb/flow/aarch64/memcmp.S
- Purpose: Optimized AArch64 `memcmp` implementation.
- Important APIs/types/functions: Exports `memcmp` through `ENTRY(memcmp)` and uses register aliases for source pointers, limit/count, loaded words, and result.
- Control flow: Handles initial 8-byte compare, fast paths for less than 8 bytes, 16-byte loop for larger inputs, optional alignment for large ranges, final overlapping last-byte comparison, and returns 0, -1, or 1 based on first differing byte order. Endianness is handled with `rev` on little-endian before comparison.
- State and persistence behavior: Pure function over memory inputs; no persistent state.
- Dependencies and integration points: Includes `asmdefs.h`, assumes ARMv8-a AArch64 with unaligned access, and overrides/provides libc-like `memcmp` for this build target.
- Risks: Correctness depends on matching C `memcmp` byte-order semantics despite word loads and endianness. Overlapping tail loads require valid memory within the compared ranges. ABI register usage and ILP32 sanitization come from macros.
- Test signals: Standard libc conformance tests should cover equal buffers, all small sizes, differing byte positions, unaligned addresses, large aligned/unaligned ranges, and both endian configurations where supported.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/aarch64/memcmp.S -->
