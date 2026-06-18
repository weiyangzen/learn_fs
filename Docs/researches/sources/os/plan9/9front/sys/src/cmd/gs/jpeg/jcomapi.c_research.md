# File Research: sources/os/plan9/9front/sys/src/cmd/gs/jpeg/jcomapi.c

Common public API shared by compression and decompression objects.

Key points:
- `jpeg_abort` releases all nonpermanent memory pools, closes temporary virtual-array storage via the memory manager, resets compressor/decompressor global state, and clears decompressor marker lists.
- `jpeg_destroy` invokes the memory manager self-destruct method, nulls the memory manager pointer, and marks the object destroyed.
- `jpeg_alloc_quant_table` and `jpeg_alloc_huff_table` allocate permanent table structs and initialize `sent_table = FALSE`.

Dependencies and interactions:
- Called by compressor/decompressor-specific abort/destroy wrappers.
- Table allocation helpers are used by parameter setup, transcoding copy, and entropy optimization.

Risk notes:
- Closing application data source/destination streams is explicitly outside these routines.
- `jpeg_abort` keeps permanent allocations for reuse; callers expecting full cleanup must call `jpeg_destroy`.
