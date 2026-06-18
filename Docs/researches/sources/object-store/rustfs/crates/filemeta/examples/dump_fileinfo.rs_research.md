# sources/object-store/rustfs/crates/filemeta/examples/dump_fileinfo.rs

Purpose: debug CLI for inspecting a single `xl.meta` file as `FileInfo`, including object parts, user/system metadata, transition fields, and compression index bytes.

Important APIs and flow: `main` reads a path argument, loads bytes, calls `get_file_info` with placeholder bucket/object names and `include_free_versions = true`, then prints size, ETag, part fields, transition fields, and sorted metadata. Part index bytes are passed to `decode_compression_index`.

Compression-index control flow: `index_candidates` tries full MinIO S2 or legacy RustFS frames when a known chunk type is present, otherwise reconstructs headerless candidates. `parse_index` validates the skippable-frame header, S2 header/trailer, length fields, signed or unsigned varints, entry limits, uncompressed-offset flag, and compressed/uncompressed offset delta coding. `restore_index_headers` rebuilds a complete skippable frame around headerless payloads. `read_varint` handles signed zig-zag decoding when requested.

State and persistence: read-only CLI over an existing xl.meta file. It reconstructs temporary candidate buffers but does not persist changes.

Dependencies and integration: uses the public `rustfs_filemeta::{get_file_info, FileInfoOpts}` path and mirrors MinIO S2 compression index formats. It is useful when investigating compatibility bugs with compressed object parts or transition metadata.

Risks: placeholder bucket/object names can affect fields derived from path context. The custom index decoder has its own bounds and varint logic, so it can diverge from production decompression code. It prints only first five and last offsets for long indexes.

Test signals: no direct tests in the example, but its helpers are deterministic and fail with explicit strings for malformed index buffers.
