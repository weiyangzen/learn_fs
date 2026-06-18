# File Research: sources/os/linux/linux-stable/fs/mpage.c

## Purpose

Provides generic multipage BIO construction for block-mapped filesystems using a `get_block_t` mapper. It batches page-cache reads and writeback into contiguous BIOs while falling back to buffer-head paths for complex mappings.

## Main Entry Points

- `mpage_readahead()`: maps readahead folios and submits read BIOs.
- `mpage_read_folio()`: reads a single folio using the same BIO-building logic.
- `__mpage_writepages()`: iterates dirty folios and writes them through `mpage_write_folio()`.
- `do_mpage_readpage()`: core read mapper/BIO builder.
- `mpage_write_folio()`: core write mapper/BIO builder.
- `mpage_read_end_io()` / `mpage_write_end_io()`: complete folio read/writeback after BIO completion.

## Control Flow And State

Read path refuses folios that already have buffers, maps logical blocks with the filesystem `get_block`, accepts only contiguous disk blocks and holes at the end of a folio, zeroes holes, and chains adjacent folios into one BIO. If it sees non-contiguous blocks, a hole followed by data, an uptodate mapped buffer supplied by the filesystem, allocation failure, or other complexity, it submits any pending BIO and falls back to `block_read_full_folio()`.

Write path either consumes existing cleanly mapped dirty buffers or maps an uptodate bufferless folio by calling `get_block(..., create=1)`. It skips whole folios beyond EOF, zeroes bytes beyond `i_size` in a partial EOF folio, builds contiguous write BIOs, marks buffers clean only after the folio is accepted into the BIO, starts writeback, and submits on boundaries or partial mappings. Complex cases fall back to `block_write_full_folio()`.

## Dependencies

Depends on Linux folios, buffer heads, BIO/block-device APIs, writeback control, backing device accounting, `get_block_t` filesystem callbacks, and generic block read/write fallback helpers.

## Risks

The fast path is intentionally narrow. Incorrectly accepting non-contiguous or partially dirty mappings would corrupt I/O completion accounting, while cleaning buffers before BIO acceptance would lose dirty data on failure. EOF zeroing is repeated during writeback because mmap can dirty bytes beyond file size. Readahead uses no-retry allocation and must degrade cleanly when BIO allocation fails.
