# File Research: sources/os/plan9/9front/sys/src/9/port/segment.c

Core Plan 9 process segment, page-table, image-cache, and segment-backed I/O implementation.

Key responsibilities:
- Allocates and frees `Segment` objects, including inline or heap segment maps.
- Frees segment pages, swap entries, profile buffers, and associated executable image references.
- Duplicates segments for fork semantics, including shared text/physical segments, copy-on-write BSS/data/stack handling, and text conversion for `TSEG`.
- Inserts pages into segment PTE maps with `segpage()` and relocates pages when moving segments.
- Maintains executable image cache by channel identity with hash and idle lists.
- Reclaims idle images and their pages under `imagereclaim()`.
- Implements `ibrk()` and `mfreeseg()` for data/BSS growth and partial segment freeing.
- Registers and finds named physical segments and implements user `segattach()`.
- Implements `segflush()`/`syssegflush()` for text-cache flushing and executable page invalidation.
- Maintains text profiling counters in `segclock()`.
- Converts between text and data segment forms via `txt2data()` and `data2txt()`.
- Implements `segio()` using a helper kernel process that temporarily maps the segment into its address space and copies data.

Dependencies:
- Uses process segment arrays, `Page`, `Pte`, swap, MMU flush, image/channel identity, and Plan 9 error infrastructure.
- Interacts with `sysproc.c` segment syscalls and `sdram.c` RAM disk I/O.

Notable behavior:
- `putseg()` holds the image lock while dropping the segment ref to prevent races with image cache reuse.
- `ibrk()` refuses to shrink a shared segment because another process may already have passed addresses to the kernel.
- `segattach()` can resolve global segments through `_globalsegattach` before looking up physical segment names.
- `segio()` copies through a bounce buffer when the caller buffer is user-space, avoiding faults in the helper process.
