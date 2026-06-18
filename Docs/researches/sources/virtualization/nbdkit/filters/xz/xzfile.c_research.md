# File Research: sources/virtualization/nbdkit/filters/xz/xzfile.c

This file abstracts liblzma index parsing and block decompression for the xz filter. `xzfile_open` allocates an `xzfile`, verifies the header magic, parses all stream indexes from the end of the file, computes stream/block counts and maximum uncompressed block size, and logs uncompressed size metadata.

`parse_indexes` mirrors xz tooling behavior: it validates file size alignment, walks backward through stream footers, skips stream padding, decodes stream footer/header flags, decodes each index with `lzma_index_decoder`, validates header/footer flag equality, stores stream flags and padding, and concatenates indexes for multi-stream files. `iter_indexes` counts non-empty blocks and tracks the largest uncompressed block.

`xzfile_read_block` locates the xz block containing an uncompressed offset, reads and decodes the block header, validates compressed size against the index, allocates the full uncompressed block buffer, streams compressed bytes through a liblzma block decoder, frees filter option allocations, and returns the decompressed block plus uncompressed start/size.

Risks and invariants: memory use scales with the xz block's uncompressed size. Error paths must clean up `lzma_stream`, indexes, filter options, and data buffers. The function reads compressed data up to the backend size and reports corrupt headers, mismatched indexes, and invalid offsets as hard failures.
