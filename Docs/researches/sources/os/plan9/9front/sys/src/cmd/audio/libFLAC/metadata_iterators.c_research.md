# File Research: sources/os/plan9/9front/sys/src/cmd/audio/libFLAC/metadata_iterators.c

## Role

`metadata_iterators.c` implements libFLAC metadata access and mutation APIs. It has three layers: level 0 convenience getters, level 1 simple file iterator operations, and level 2 in-memory metadata chains plus chain iterators. It reads, writes, inserts, deletes, pads, and rewrites FLAC metadata blocks.

## Level 0: Convenience Getters

`get_one_metadata_block_()` creates a stream decoder, disables MD5 checking, asks for one metadata type, and clones the matching metadata block from the decoder callback. Public wrappers expose `FLAC__metadata_get_streaminfo()`, `FLAC__metadata_get_tags()`, `FLAC__metadata_get_cuesheet()`, and `FLAC__metadata_get_picture()`.

`FLAC__metadata_get_picture()` scans picture blocks with the simple iterator and selects the largest matching image by area, using depth as a tie-breaker.

## Level 1: Simple Iterator

`FLAC__Metadata_SimpleIterator` owns a `FILE *`, filename, optional temp path prefix, saved file stats, current block offset, first STREAMINFO offset, current block header fields, and a small offset stack for push/pop navigation.

Important operations:

- `FLAC__metadata_simple_iterator_init()` opens a file read-write when possible, otherwise read-only, finds the FLAC signature, and verifies the first metadata block is STREAMINFO.
- `next()` and `prev()` traverse metadata blocks by seeking over block lengths.
- `get_block()` allocates a `FLAC__StreamMetadata`, reads current block data, then seeks back to the block data start.
- `set_block()`, `insert_block_after()`, and `delete_block()` either write in place, split or consume padding, or rewrite the whole file through a temp file.
- `rewrite_whole_file_()` copies prefix, writes replacement or inserted metadata, copies postfix, fixes `is_last` flags when needed, renames the temp file over the original, and re-primes the iterator.

STREAMINFO replacement is constrained: replacing STREAMINFO with a different type, or inserting STREAMINFO, is rejected.

## Level 2: Chains

`FLAC__Metadata_Chain` stores metadata blocks as a doubly linked list of `FLAC__Metadata_Node`. Chain reading supports native FLAC by parsing metadata directly and Ogg FLAC by using a stream decoder callback path. Ogg chain writing is explicitly unsupported.

Important chain operations:

- `chain_read_cb_()` parses all metadata blocks into nodes and records first/last offsets and initial chain length.
- `chain_prepare_for_write_()` adjusts padding to avoid a whole-file rewrite when possible, adds or trims terminal padding, and rejects non-padding metadata blocks that exceed FLAC’s 24-bit metadata length field.
- `FLAC__metadata_chain_check_if_tempfile_needed()` mirrors the write-preparation sizing logic without mutating the chain.
- `FLAC__metadata_chain_write()` writes metadata in place if length is unchanged; otherwise it rewrites via temp file.
- Callback write APIs enforce correct use: in-place callback write must not need a temp file, while temp-file callback write must need one.
- `FLAC__metadata_chain_sort_padding()` moves padding blocks to the end, then merges adjacent padding.

`FLAC__Metadata_Iterator` navigates and mutates the in-memory chain. It cannot delete or insert before the first STREAMINFO block, and it rejects insertion of STREAMINFO elsewhere.

## Metadata Parsing and Serialization

The file implements local big-endian and little-endian pack/unpack helpers. It reads and writes all standard FLAC metadata types:

- STREAMINFO
- PADDING
- APPLICATION
- SEEKTABLE
- VORBIS_COMMENT
- CUESHEET
- PICTURE
- UNKNOWN/opaque blocks

Vorbis comment lengths are little-endian; most FLAC structure fields are big-endian. Padding is skipped on read and emitted as zero-filled blocks on write. Unknown blocks are preserved as opaque bytes.

The FLAC signature scanner skips an optional ID3v2 tag before checking for `fLaC`.

## File Rewrite and Platform Behavior

Temp files default to `<filename>.metadata_edit`. `transport_tempfile_()` closes the temp file and renames it over the original, with Windows-specific unlink-before-rename handling. Comments note that `tempfile_path_prefix` support is incomplete because cross-filesystem movement would require copy rather than rename.

`get_file_stats_()` and `set_file_stats_()` preserve mode and times, and on non-Windows-like builds attempt owner/group restoration via `chown()`. File I/O is routed through compatibility wrappers such as `flac_fopen`, `flac_rename`, `flac_unlink`, `flac_stat`, `flac_chmod`, and `flac_utime`.

## Risks / Edge Cases

- `write_metadata_block_stationary_with_padding_()` returns `FLAC__METADATA_SIMPLE_ITERATOR_STATUS_MEMORY_ALLOCATION_ERROR` from a `FLAC__bool` function when padding allocation fails, without setting iterator status. Since that enum value is nonzero, this can be misread as success and should be verified against upstream or tested.
- `read_metadata_block_data_application_cb_()` reads the 4-byte application ID before checking whether `block_length` is at least 4.
- Vorbis comment parsing is intentionally lenient: malformed lengths can cause the parser to skip remaining bytes and still return OK after preserving partial data.
- Ogg FLAC chain offsets are marked as wrong placeholders, and write-back for Ogg FLAC returns internal error.
- The temp-file replacement path is rename-based and not crash-atomic in the stronger transactional sense.
- Many invariants rely on assertions: valid initialized iterators, non-null callbacks, STREAMINFO first, sane block sizes, and small push depth.

## Dependencies

Uses `private/metadata.h`, `FLAC/stream_decoder.h`, `FLAC/assert.h`, `share/alloc.h`, `share/compat.h`, `share/macros.h`, `share/safe_str.h`, `private/macros.h`, and `private/memory.h`. It aliases `safe_malloc_mul_2op_` to `safe_malloc_mul_2op_p` from `memory.c`.
