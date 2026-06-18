# sources/sync-backup/casync/src/cachunk.c

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/casync/src/cachunk.c -->
## sources/sync-backup/casync/src/cachunk.c

Purpose: `cachunk.c` implements chunk load/save helpers, compression/decompression wrappers, and sharded chunk-file storage operations. It is central to reading and writing casync chunk payloads in compressed or uncompressed form.

Important APIs and functions: `ca_load_fd`, `ca_load_and_decompress_fd`, and `ca_load_and_compress_fd` read fd contents into `ReallocBuffer`. `ca_save_fd`, `ca_save_and_compress_fd`, and `ca_save_and_decompress_fd` write data to fds. `ca_compress` and `ca_decompress` operate in memory. Chunk-file APIs include `ca_chunk_file_open`, `ca_chunk_file_test`, `ca_chunk_file_load`, `ca_chunk_file_save`, `ca_chunk_file_mark_missing`, and `ca_chunk_file_remove`.

Control flow: load/save functions enforce min/max chunk sizes and stream through `CompressorContext`. Detection uses `detect_compression` before decoding. Chunk paths are formatted as `<prefix><first4>/<fullid><suffix>`. Saves first test for existing chunks, write a random `.tmp` suffixed file, transform data if requested, then rename without replacement to the final suffix. Loads try the desired representation first and fall back to the alternate representation, converting as needed. Missing chunks are represented by symlinks to `/dev/null`; open with `O_NOFOLLOW` returns `-ELOOP`, translated to `-EADDRNOTAVAIL`.

State and persistence: persistent state is the chunk store directory, shard directories, immutable read-only chunk files, compressed chunk suffix variants, temporary files, and missing-marker symlinks. Temporary files are unlinked on failure.

Dependencies and integration points: depends on `cachunkid`, `cacompression`, `compressor`, `cautil`, `def`, `realloc-buffer`, and utility wrappers such as `loop_write`, `rename_noreplace`, and `random_u64`. Compression availability depends on build-time feature macros.

Risks: decompression and compression limits are security-critical. Some paths return `-EINVAL` where preserving the original unlink error might be more diagnostic, notably `ca_chunk_file_remove` after uncompressed unlink failures other than `ENOENT`. `ca_load_and_decompress_fd` appears to return `0` if `compressor_input` fails inside the main loop, which may mask an error. Race handling relies on no-replace rename and immutable files.

Test signals: tests should cover round-trips for every compression type, load fallback between compressed and uncompressed storage, max-size rejection, empty chunk rejection, missing-marker behavior, duplicate save returning `-EEXIST`, temp cleanup on transform errors, and removal of both suffix variants.
<!-- END_FILE_RESEARCH: sources/sync-backup/casync/src/cachunk.c -->
