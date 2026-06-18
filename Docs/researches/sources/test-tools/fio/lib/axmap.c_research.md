# sources/test-tools/fio/lib/axmap.c

Purpose: implements a hierarchical bitmap set optimized for tracking used/free block numbers. Higher levels mark full words in lower levels, making full maps cheaper to search.

Important APIs/functions: `axmap_new`, `axmap_free`, `axmap_reset`, `axmap_set`, `axmap_set_nr`, `axmap_isset`, and `axmap_next_free`. Internal helpers walk levels bottom-up or top-down, set contiguous bits up to a word boundary, and find the first free bit with wraparound support.

Control flow: construction computes the number of levels from `nr_bits`, allocates one map per level, and zeroes them. Setting a bit updates level 0 and then propagates one-bit fullness indicators upward. `axmap_next_free` first checks the current level-0 word and then performs a top-down search, wrapping to zero if needed.

State/persistence: state is entirely in heap-allocated `struct axmap` levels and unsigned-long maps. No locking is present; callers must serialize concurrent updates.

Dependencies/integration: depends on architecture `BITS_PER_LONG`, `ffz`, `types.h` bool, and `min`. It is suitable for fio random maps and allocator-style free-slot discovery.

Risks/test signals: boundary handling around `bit_nr == nr_bits` and partial final words is delicate; `axmap_isset` uses `<= nr_bits`, which deserves attention because valid bits end at `nr_bits - 1`. Tests should cover 32/64-bit builds, full maps, wraparound, contiguous set truncation, and repeated duplicate sets.
