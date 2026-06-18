# File Research: sources/os/bsd/freebsd-src/sys/sys/memdesc.h

Defines an abstract memory descriptor used to represent different backing layouts for I/O buffers.

Key content:
- `struct memdesc` stores one of: virtual address, physical address, bus DMA segment list, UIO, mbuf, VM page array, plus length/segment count/offset and type.
- Types include contiguous virtual, contiguous physical, virtual scatter/gather list, physical scatter/gather list, UIO, mbuf, and VM pages.
- Inline constructors: `memdesc_vaddr`, `memdesc_paddr`, `memdesc_vlist`, `memdesc_plist`, `memdesc_uio`, `memdesc_mbuf`, `memdesc_vmpages`.
- Conversion constructors declared for `bio` and CAM `ccb`.
- Declares copy helpers `memdesc_copyback` and `memdesc_copydata`.
- Defines callback types for allocating external-buffer mbufs and ext-page mbufs.
- `memdesc_alloc_ext_mbufs()` constructs an mbuf chain backed by the described memory, using `M_EXT` for mapped storage and `M_EXTPG` for unmapped/page storage; supports offset, length, actual length, wait flag, and truncation.

Research relevance:
- Bridges storage I/O (`bio`, CAM CCB), VM pages, UIO, and network mbufs.
- Important for zero-copy or low-copy paths, sendfile-like logic, and storage/network integration.
- Tightly related to `mbuf.h` external storage and unmapped page semantics.

Cautions:
- A memdesc is only a description; caller-supplied callbacks manage actual mbuf allocation and references.
- Partial allocation failure frees already-built chains.
- Truncation can intentionally return a shorter chain to avoid splitting pages.
