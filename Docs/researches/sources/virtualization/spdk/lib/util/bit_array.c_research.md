# File Research: sources/virtualization/spdk/lib/util/bit_array.c

This file implements SPDK dynamic bit arrays and a bit-pool allocator built on top of them.

`spdk_bit_array_resize()` uses 64-bit words, rejects `UINT32_MAX` capacity because that sentinel means not-found, and allocates one extra sentinel word. The sentinel is set to `0b10`, allowing `find_first_set` and `find_first_clear` to scan without explicit loop bounds and still detect end-of-array. Growing zeroes new words; shrinking clears now-out-of-range bits in a partial final word.

Bit-array APIs support create/free, capacity, get/set/clear, find-first-set, find-first-clear, count set/clear bits, store/load masks, and clear-mask. Out-of-range get returns false, set returns `-EINVAL`, and clear is a no-op.

`spdk_bit_pool` wraps a bit array with `lowest_free_bit` and `free_count`. It supports create, create from existing array, free, resize, capacity, allocation status, allocate next free bit, mark a specific bit allocated, free a bit, count allocated/free, store/load mask, and free all bits. Allocation updates `lowest_free_bit` by scanning from the allocated position; freeing lowers it when appropriate.

Important invariants are the sentinel extra word, keeping bits past `bit_count` clear, `free_count` matching the underlying mask, and only freeing allocated pool bits. There is a small cleanup issue in `ublk_ios_init` style not here; in this file the main risk is that mask load/store assumes caller-provided buffers are large enough for the bit capacity.
