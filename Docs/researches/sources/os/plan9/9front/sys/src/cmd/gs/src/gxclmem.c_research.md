# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxclmem.c

Implements the RAM-backed command-list file abstraction. It provides file-like open/write/read/seek/close operations backed by logical blocks, physical memory blocks, optional LZW compression, reserve blocks for low-memory guarantees, and an LRU decompression cache.

Key behavior:
- Stores data in `LOG_MEMFILE_BLK` logical blocks pointing to `PHYS_MEMFILE_BLK` physical blocks; initially each logical block has a raw physical block.
- Begins compression once total allocated space exceeds `COMPRESSION_THRESHOLD`, compressing prior full logical blocks and leaving the current block raw for writing.
- `allocateWithReserve` first tries normal allocation, then falls back to preallocated reserve blocks, returning a positive low-memory warning when reserve storage is consumed.
- `memfile_fopen` only supports creating new write-mode scratch files, allocates the `MEMFILE`, initializes an empty file, reserves initial warning space, and allocates compressor/decompressor stream states from the LZW prototypes.
- `memfile_set_memory_warning` preallocates enough logical and physical reserve blocks to guarantee a later write budget after a low-memory warning.
- `compress_log_blk` compresses one full logical block into the current compressed physical chain, allowing at most one additional physical block for overflow.
- `memfile_next_blk` advances to a new logical block, allocating raw blocks before compression starts or compressing the previous block and reusing its raw block after compression starts.
- `memfile_fwrite_chars` appends data, reinitializing the file when writing from offset zero and truncating length to the new write position.
- `memfile_get_pdata` resolves the current logical block into raw readable data, either by direct pointer for uncompressed blocks or by decompressing into an LRU raw-buffer cache.
- The raw decompression cache allocates roughly one buffer per 32 logical blocks, with a minimum of 8 if possible, and moves accessed buffers to the head.
- Handles compressed logical data spanning a second physical block by copying remainder bytes into `data_spare` before continuing decompression.
- `memfile_fread_chars`, `memfile_rewind`, and `memfile_fseek` implement sequential and forward-biased random access over the logical block chain.
- `memfile_free_mem` releases compressed physical chains, uncompressed physical blocks, logical blocks, raw buffers, and stream internal state; comments document rejected/freeing algorithms and the chosen correct one.
- `memfile_init_empty` creates the initial raw physical/logical block pair and resets file state.

Dependencies:
- Implements the `gxclio.h` clist file API through aliases declared in `gxclmem.h`.
- Uses Ghostscript memory allocation, stream cursors/templates, and compression prototypes from `gxcllzw.c`.

Research notes:
- Partial overwrite is intentionally unsupported except for rewinding to the beginning; a write after seeking into the middle reports a truncate problem but lacks full cleanup logic.
- Compression assumes a source logical block will not require more than two destination physical blocks; exceeding that is treated as fatal.
- Low-memory reserve accounting is central to clist recovery: positive write statuses mean success with a warning, not failure.
