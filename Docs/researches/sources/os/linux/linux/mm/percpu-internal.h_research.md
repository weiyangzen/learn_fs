# File Research: sources/os/linux/linux/mm/percpu-internal.h

Internal per-CPU allocator definitions shared by the percpu core, vmalloc backend, kernel-memory backend, and debug statistics code.

Key responsibilities:
- Defines `pcpu_block_md`, the bitmap-block metadata used for allocation scan hints and contiguous free-space hints.
- Defines optional per-object extension storage for memcg and allocation profiling metadata.
- Defines `struct pcpu_chunk`, including allocation/free bitmaps, chunk metadata, base address, populated bitmap, object extensions, and debug counters.
- Declares global percpu allocator state such as chunk lists, slot indices, first/reserved chunks, and the allocator spinlock.
- Provides conversion helpers between pages, bitmap bits, metadata blocks, and full accounted object size.
- Defines `struct percpu_stats` and inline stats update helpers when `CONFIG_PERCPU_STATS` is enabled.
- Provides no-op stats helpers when percpu stats are disabled.

Important behavior:
- Allocation maps operate in units of `PCPU_MIN_ALLOC_SIZE`; metadata block counts derive from physical pages served by the chunk.
- `pcpu_obj_full_size()` accounts for all possible CPUs and optional object cgroup extension storage.
- Stats updates for allocation/deallocation require `pcpu_lock`; chunk allocation/deallocation helpers take the lock internally.
- `need_pcpuobj_ext()` enables object extensions when memcg kmem accounting or memory allocation profiling requires them.

Dependencies:
- Uses percpu allocator public definitions, memcg state, optional memory allocation profiling tags, spinlocks, and chunk list globals provided by the main percpu allocator implementation.

Notable risks:
- The chunk layout is cacheline-conscious; changing fields can affect false sharing on allocator hot paths.
- Bitmap conversion helpers must stay consistent with `PCPU_MIN_ALLOC_SIZE`, `PCPU_BITMAP_BLOCK_SIZE`, and populated page accounting.
