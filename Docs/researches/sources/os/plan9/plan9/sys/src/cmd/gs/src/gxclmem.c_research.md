# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxclmem.c

## Purpose
Implements RAM-backed command-list “files” with optional LZW compression, reserve memory, seeking, reading, and writing.

## Main Responsibilities
- Implements `memfile_fopen`, `memfile_fclose`, `memfile_fwrite_chars`, `memfile_fread_chars`, `memfile_fseek`, `memfile_rewind`, and status helpers.
- Maintains logical blocks mapped to physical data blocks.
- Starts compression after a threshold of allocated data.
- Caches decompressed blocks in an LRU raw-buffer list.
- Provides reserve-block behavior so clist writes can complete after low-memory warnings.

## Data Model
- `LOG_MEMFILE_BLK`: logical file block used for file-position indexing.
- `PHYS_MEMFILE_BLK`: physical storage block holding raw or compressed data.
- `RAW_BUFFER`: decompression cache entry.
- `MEMFILE`: full memory file state, including allocators, logical position, compression streams, reserves, and read/write cursors.

## Key Implementation Details
- Uncompressed mode uses one physical block per logical block.
- When `NEED_TO_COMPRESS` becomes true, earlier full logical blocks are compressed into chained physical blocks.
- The last block remains raw while writing.
- Compressed logical blocks remember their physical block and byte pointer.
- Decompression uses a lazily allocated raw-buffer pool sized roughly one buffer per 32 logical blocks, with a minimum of 8.
- `memfile_get_pdata` resolves the current logical block into readable raw bytes, using the decompression cache when necessary.
- Backward seeks restart traversal from the logical head; forward seeks traverse from current state.

## Memory-Pressure Behavior
- `memfile_set_memory_warning` preallocates reserve logical and physical blocks.
- `allocateWithReserve` falls back to reserve chains and returns positive status for low-memory warning success.
- `memfile_fwrite_chars` stores positive warning status in `error_code` but can still report full byte count written.

## Limitations
- Reopening existing memory files is not implemented.
- Closing without deletion is rejected.
- `unlink` is not representable because memfiles are only identified by pointer.
- Writing after seeking to non-start positions is not properly supported; the code expects clist usage patterns.

## Dependencies
- `gxclmem.h` for structure declarations and API aliases.
- LZW prototypes from `gxcllzw.c`.
- Ghostscript stream templates and memory allocators.

## Research Notes
This is a custom in-memory file layer for band-list storage. It is optimized around sequential writes, mostly increasing-position reads, and bounded low-memory recovery rather than general file semantics.
