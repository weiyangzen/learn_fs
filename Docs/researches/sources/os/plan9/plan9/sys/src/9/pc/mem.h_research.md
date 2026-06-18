# File Research: sources/os/plan9/plan9/sys/src/9/pc/mem.h

- Size/hash: 162 lines, 5569 bytes, SHA-256 `01e23fdd85c437f1ce555f38e6453fccaaa6fc450fad83ddcc7cbc141aa5c7d2`.
- Purpose: Shared x86 memory, address-space, segment, and page-table constants for C and assembly.
- Basic constants: Defines word/page sizes, page shift, cache-line size, block alignment, FPU save alignment, `MAXMACH`, and `KSTACK`.
- Time constants: Defines `HZ`, `MS2HZ`, and `TK2SEC`.
- Address layout: Defines `KZERO = 0xF0000000`, `KTZERO`, virtual page-table area `VPT`, `KMAP`, `VMAP`, user base/text/stack constants, `USTKSIZE`, and exec stack sizing.
- Reserved low/kernel addresses: Defines `CONFADDR`, `TMPADDR`, `APBOOTSTRAP`, `RMUADDR`, `RMCODE`, `RMBUF`, `IDTADDR`, `REBOOTADDR`, bootstrap CPU page directory/page tables/GDT/Mach addresses, and `CPU0END`.
- Segmentation: Defines GDT segment indices, selectors, descriptor type bits, privilege/present/granularity flags, and data/code readability/writability bits.
- MMU constants: Defines virtual segment-map sizes, PPN masking, PTE valid/write/user/cache/global/large-page bits, and `PDX`/`PTX` index macros.
- Dependencies: Used directly by `l.s`, MMU code, boot code, and machine-dependent C files. Values are ABI-like across boot, assembly, and C.
- Research notes: Critical to virtual memory and boot layout. Filesystem relevance is indirect but fundamental: page, kmap, and user/kernel layout constants constrain buffer, cache, process, and device-memory behavior.
