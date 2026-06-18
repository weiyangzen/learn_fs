# File Research: sources/os/bsd/openbsd-src/sys/sys/hibernate.h

This header defines hibernation image metadata, allocator state, compression state, and suspend/resume functions.

Key definitions:
- Limits/flags: `HIB_PHYSSEG_MAX`, `HIBERNATE_CHUNK_USED`, `CONFLICT`, `PLACED`, `HIBERNATE_MAGIC`, `HIB_MOVE`, `HIB_SKIP`.
- Allocator: `struct hiballoc_arena`.
- Compression: `struct hibernate_zlib_state`.
- Memory/disk image pieces: `hibernate_memory_range`, `hibernate_disk_chunk`.
- IO operation constants and callback type: `HIB_INIT`, `HIB_DONE`, `HIB_R`, `HIB_W`, `hibio_fn`.
- `union hibernate_info`, padded to 4096 bytes, with magic, device, physical memory ranges, image/chunk offsets, piglet addresses, IO function/page, kernel hash, stack guard fields, return guard offset, and sector size.

APIs:
- Hibernate allocator: `hib_alloc`, `hib_free`, `hiballoc_init`.
- Physical memory helpers: `uvm_pmr_dirty_everything`, `uvm_pmr_alloc_pig`, `uvm_pmr_alloc_piglet`, `uvm_page_rle`, `uvmpd_hibernate`.
- IO/info: `get_hibernate_io_function`, `get_hibernate_info`, `hibernate_block_io`, `hibernate_write`.
- Compression/image: `hibernate_zlib_reset`, allocation hooks, inflate/deflate/process/read/unpack functions.
- Signature/chunk operations, suspend/resume, memory preallocation, entropy, bufcache suspend/resume.

Risk notes:
- `union hibernate_info` is constrained to a disk sector-sized signature block.
- Resume correctness depends on physical address ranges, chunk placement, compression state, and kernel hash/guard metadata matching the saved image.
