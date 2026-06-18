# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/jcomapi.c

Common public API helpers shared by compression and decompression.

Key behavior:
- `jpeg_abort` frees all nonpermanent memory pools, resets compressor/decompressor state for reuse, and clears decompressor marker lists.
- `jpeg_destroy` delegates full cleanup to the memory manager and marks the object destroyed.
- Provides permanent-pool allocation helpers for quantization and Huffman table structs, clearing `sent_table` so new tables will be emitted.

Dependencies:
- Uses the common JPEG memory manager interface and state constants for compressor/decompressor objects.

Notable risks:
- Application-owned source/destination streams and top-level structs are not closed or freed here.
- `jpeg_abort` assumes temporary virtual arrays never live in the permanent pool, matching IJG memory-manager design.
