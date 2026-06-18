# File Research: sources/os/linux/linux/fs/mpage.c

## Purpose
Provides generic multipage BIO assembly for block-mapped filesystems. It batches page-cache folios into larger BIOs for readahead, read-folio, and writeback when logical file blocks map to contiguous disk blocks.

## Main Responsibilities
- Submit multipage read and write BIOs.
- End read/write folio I/O on BIO completion.
- Build read BIOs for fully or partially mapped folios.
- Fall back to buffer-head based I/O for non-contiguous, holey, buffered, or otherwise complex folios.
- Build write BIOs for fully mapped dirty folios.
- Integrate with generic writeback iteration and cgroup writeback accounting.

## Key Functions
- `mpage_read_end_io()` ends read on every folio in a completed read BIO.
- `mpage_write_end_io()` records mapping errors and ends writeback for each folio in a write BIO.
- `mpage_bio_submit_read()` / `mpage_bio_submit_write()` install completion handlers, guard end-of-device, submit BIOs, and return `NULL`.
- `map_buffer_to_folio()` transfers a mapped/up-to-date buffer-head mapping into folio buffers or marks a same-size folio uptodate.
- `do_mpage_readpage()` maps blocks for one folio, builds contiguous read BIOs, zeroes holes at EOF, or falls back to `block_read_full_folio()`.
- `mpage_readahead()` loops over readahead folios and submits accumulated read BIOs.
- `mpage_read_folio()` reads one folio through the same path.
- `clean_buffers()` clears dirty bits for buffers covered by an outgoing write and may free buffer heads.
- `mpage_write_folio()` maps or validates one dirty folio and adds it to a write BIO or falls back to `block_write_full_folio()`.
- `__mpage_writepages()` iterates dirty folios with `writeback_iter()`, optionally delegates first to a filesystem callback, then writes through `mpage_write_folio()`.

## Read Path Behavior
The read path avoids attaching buffer heads unless necessary. It reuses previous `get_block()` results when possible, maps logical blocks for the folio, checks for holes and contiguity, zero-fills holes at EOF, and appends fully suitable folios to a BIO. If a folio already has buffers, contains a hole before non-hole data, has non-contiguous mappings, needs buffer-up-to-date handling, or cannot allocate a BIO, it falls back to `block_read_full_folio()`.

`BH_Boundary` causes accumulated BIOs to be submitted before metadata-dependent future mappings, preserving better disk request order around indirect-block reads.

## Write Path Behavior
The write path accepts folios only when dirty data is fully mapped and contiguous, with a special EOF case for unmapped tail blocks. For folios without buffers, it calls `get_block(..., create=1)` to allocate mappings. It zeroes data beyond `i_size`, submits existing BIOs when disk contiguity breaks, cleans covered buffers only after successfully adding the folio to a BIO, starts writeback, unlocks the folio, and handles boundary blocks.

## Important Behaviors and Edge Cases
- The code avoids multipage BIOs for partial/non-contiguous cases because page completion across multiple BIOs is complex.
- Readahead uses `REQ_RAHEAD` and more conservative GFP flags.
- Whole folios beyond EOF are skipped through fallback handling to avoid allocating blocks past EOF.
- Partial EOF folios are zeroed on every writepage invocation because mmap exposes zeroed bytes beyond file size.
- `buffer_boundary()` triggers BIO submission and optional boundary block write.
- Write fallback records mapping errors from `block_write_full_folio()`.
- `__mpage_writepages()` uses `blk_plug` to improve block-layer batching.

## Dependencies
- Filesystem-supplied `get_block_t`.
- Buffer-head fallback helpers.
- BIO, block device, writeback, folio, readahead, and cgroup writeback infrastructure.

## Research Notes
This file is a generic library used by simple block-mapped filesystems such as Minix. It optimizes the common contiguous mapping case and intentionally delegates complicated buffer states to older buffer-head paths.
