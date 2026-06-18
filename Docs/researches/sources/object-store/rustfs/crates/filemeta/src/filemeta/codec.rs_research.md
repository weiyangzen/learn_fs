# sources/object-store/rustfs/crates/filemeta/src/filemeta/codec.rs

Purpose: binary codec for the top-level `FileMeta` XL2 on-disk format.

Important APIs/functions: `is_xl2_v1_format`, `load`, `read_format_versions`, `check_xl2_v1`, `is_indexed_meta`, `read_bytes_header`, `unmarshal_msg`, private `decode_xl_headers`/`decode_versions`, `is_latest_delete_marker`, and `marshal_msg`.

Control flow: decoding validates the `XL2 ` magic, reads little-endian major/minor file version, reads a MessagePack bin length, splits metadata payload, reads a MessagePack u32 CRC, verifies xxhash64-truncated CRC over metadata, validates optional inline data, decodes header/meta version/count, then iterates header and version-meta bin pairs into `FileMetaShallowVersion`. `is_latest_delete_marker` decodes only enough metadata to inspect the first header and uses `Error::DoneForNow` as early exit. Encoding writes magic/version, reserves a bin32 length, writes header version, meta version, version count, each version header/meta as bins, patches the metadata length, appends CRC, then appends inline data bytes.

State and persistence: this module defines persisted byte layout and checksum validation. It mutates `self.data`, `self.meta_ver`, and `self.versions` during unmarshal. The metadata CRC protects only the metadata payload, not trailing inline data, which is validated by `InlineData::validate`.

Dependencies and integration: uses `byteorder`, `rmp`, `xxhash_rust`, `Cursor`, `Read`, `Write`, `FileMetaVersionHeader`, and `InlineData`. `read_format_versions` supports compatibility tests and tooling without full object decode.

Risks: the format assumes the MessagePack bin length prefix is exactly five bytes in several helpers. Major versions greater than the current major are rejected, but minor is not bounded. `is_indexed_meta` returns empty slices for unsupported/short metadata in some cases, so callers must treat empty as "not indexed" rather than valid parse. Inline data integrity relies on its own validator.

Test signals: library tests exercise real/legacy format version reads, round-trip marshal/load, CRC/corruption failures, latest delete marker checks indirectly, and async no-data reads.
