# sources/sync-backup/borg/src/borg/chunkers/fixed.py

Purpose: implements `ChunkerFixed`, a fixed-size chunker for data with stable offsets such as disk images, block devices, or simple record-oriented database files.

Important APIs: `ChunkerFixed(block_size, header_size=0, sparse=False)` configures block size, optional first header chunk size, sparse/file-map reading, and `chunking_time`. `chunkify(fd=None, fh=-1, fmap=None)` creates a `FileReader`, optionally yields a header chunk read with `header_size`, then repeatedly reads up to `block_size` and yields chunks until a zero-size chunk indicates EOF.

Control flow and state: the chunker stores its `FileReader` on `self.reader` and accumulates monotonic-time spent in reads. It asserts each yielded non-header chunk is no larger than `block_size`; the last chunk in a data or hole range may be smaller.

Dependencies and integration: depends on `.reader.FileReader` for sparse and file-map behavior. Constructed by `get_chunker("fixed", ...)` and used anywhere fixed chunker params are selected, including transfer rechunking or create paths.

Risks: correctness rests on `FileReader` returning chunks with `meta["size"]`; a malformed reader result can trip assertions. Fixed chunking intentionally gives no content-defined boundary shifts, so insertions near the beginning can reduce deduplication versus buzhash.

Test signals: cover no-header and header modes, file descriptor/file object inputs, sparse and fmap reads, empty files, partial final chunks, timing accumulation, and assertion behavior for overlarge reader chunks.
