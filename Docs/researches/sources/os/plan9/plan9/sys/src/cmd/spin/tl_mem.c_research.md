# File Research: sources/os/plan9/plan9/sys/src/cmd/spin/tl_mem.c

Pool allocator for Spin's LTL translator.

Key responsibilities:
- Allocates small fixed-size chunks from per-size freelists.
- Tracks allocation statistics by size class.
- Frees small allocations back to freelists; large allocations are intentionally not returned to libc.
- Maintains `All_Mem` accounting.

Important functions:
- `tl_emalloc`: rounds requested bytes to `union M` units, allocates blocks in growing batches, clears memory, and tags blocks with `A_USER`.
- `tfree`: validates allocation tag and returns small blocks to freelist.
- `a_stats`: prints pool/allocation/free counters.

Notable details:
- Size classes below `A_LARGE` are pooled.
- Batch sizes grow until `NOTOOBIG`.
- Large frees are logged but not actually freed.

Risks/quirks:
- Not thread-safe.
- Free validation only checks a magic high-byte tag.
- Designed for short-lived translator runs where leaking large blocks is acceptable.
