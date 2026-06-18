# File Research: sources/os/bsd/openbsd-src/sys/kern/subr_hibernate.c

## Role

Implements machine-independent OpenBSD hibernate suspend/resume support. It records machine and swap metadata, compresses physical memory into swap, writes chunk metadata and a signature block, validates a saved image during boot, reads it into a safe pig area, and restores memory using machine-dependent resume hooks.

## Key Behavior

- Defines the piglet layout: I/O pages, copy/RLE pages, final chunk ordering, hiballoc/zlib workspace, preserved entropy, retguard preservation, chunk table, and bounce area.
- `hibernate_write()` bounds-checks writes to image, chunk table, or signature areas before invoking the device-specific hibernate I/O function.
- `get_hibernate_info()` records hibernate device, disklabel-derived swap signature location, sector size, kernel hash, piglet addresses, I/O hooks, memory ranges, and machine-dependent metadata.
- `preallocate_hibernate_memory()`, `uvm_pmr_alloc_piglet()`, and `uvm_pmr_alloc_pig()` allocate DMA-safe piglet/pig memory while avoiding overlap with resume scratch areas.
- The `hiballoc` arena provides a tiny aligned allocator used by zlib during suspend/resume when normal allocation is unsafe.
- `uvm_pmr_dirty_everything()` clears `PG_ZERO` state after resume because restored memory invalidates assumptions about pre-zeroed free pages.
- `uvm_page_rle()`, `hibernate_calc_rle()`, and `hibernate_write_rle()` encode free-page runs so free physical pages do not need full page data in the compressed image.
- `hibernate_write_chunks()` splits physical memory ranges into hibernate chunks, resets zlib per chunk, writes RLE tokens and page data, records compressed sizes, and updates the chunk table.
- `hibernate_write_chunktable()`, `hibernate_write_signature()`, and `hibernate_clear_signature()` persist or clear metadata in swap.
- `hibernate_resume()` reads and clears the signature, compares memory/kernel signatures, quiesces CPUs/devices, handles stack protector/retguard preservation, switches stacks, and calls unpack.
- `hibernate_read_image()` reads the chunk table, totals compressed image size, allocates pig memory, reads chunks, and prepares resume page tables.
- `hibernate_read_chunks()` orders chunks so non-overlapping regions are restored first, reads compressed chunks into the pig area, and stores final ordering in the piglet.
- `hibernate_unpack_image()`, `hibernate_process_chunk()`, `hibernate_copy_chunk_to_piglet()`, `hibernate_inflate_region()`, and `hibernate_inflate_page()` switch into resume mappings, inflate chunk streams, skip or move special pages, and finally jump to the MD resume vector.
- `hibernate_suspend()` obtains hibernate info, finds swap space, calculates image/chunk offsets, writes chunks, chunk table, and signature, then sends final I/O cleanup notification.
- `hibernate_alloc()` and `hibernate_free()` map/unmap temporary hibernate pages around suspend work.

## Interfaces And Dependencies

Depends on UVM physical memory/page queues, swap metadata, disklabel reads, block device strategy I/O, zlib, SHA256, pmap mapping primitives, machine-dependent hibernate hooks, stack protector guard state, retguard symbols, autoconf device suspend, and swap device globals.

## Notes

The implementation is highly order-sensitive. After interrupts are disabled and resume mappings are active, normal kernel services and global data cannot be assumed safe. The signature is cleared before attempting resume to avoid repeated failed resumes.
