# sources/object-store/openstack-swift/swift/common/ring/io.py

## Purpose
`io.py` implements low-level ring file I/O. It wraps gzip streams to support deterministic atomic writes, seekable reads at full-flush boundaries, version detection, v2 named sections, section checksums, length-value blobs, JSON blobs, and network-order ring assignment tables.

## Important APIs, types, and functions
`_RingGzReader` reads bounded amounts from a gzip/deflate stream and supports compressed-position seeking. `SectionReader` limits reads to a section and verifies full consumption and checksum on close. `IndexEntry` records compressed/uncompressed section offsets and checksum metadata. `RingReader` validates the `R1NG` magic, records version, loads v2 indexes, reads blobs, and opens named sections. `_RingGzWriter` writes gzip data to a temporary file and atomically renames it on successful close. `RingWriter` adds magic/version writing, named `section()` contexts, `write_size()`, `write_blob()`, `write_json()`, `write_ring_table()`, and `write_index()`.

## Control flow and state behavior
Readers buffer compressed input until zlib full-flush markers so they can reset decompressors and seek to section boundaries. `RingReader.__init__()` reads magic/version, records gzip sizes, loads the v2 index if present, then seeks back to the beginning. For v2, the index start is found near the gzip tail; entries are sorted by compressed offset and stored as an ordered dict. Opening a section seeks to the compressed start, verifies the blob length against index metadata, creates the requested checksum, and yields a `SectionReader`.

Writers create a temp file in the destination directory, finalize gzip only on successful context exit, fsync, chmod to `0644`, and rename atomically. `RingWriter.section()` prevents nested/duplicate/invalid sections, records start offsets, hashes data written in the section, and records end offsets/checksum. If any sections exist, `close()` writes a JSON index and both uncompressed and compressed index offsets at the end.

## Dependencies and integration points
This module depends on `gzip`, `zlib`, `hashlib`, `json`, `struct`, `dataclasses`, `tempfile`, and ring utility functions for network-order arrays. `RingData.load()` and `RingData.save()` use `RingReader` and `RingWriter`. V2 sections are named `swift/ring/metadata`, `swift/ring/devices`, and `swift/ring/assignments` by `ring.py`.

## Risks and edge cases
The reader refuses greedy `read(-1)`, so callers must know sizes. Seeking only works safely to full-flush boundaries; recompressing a ring can break v2 index seeking. `SectionReader.read()` assumes a checksum object is present and updates it unconditionally. `IndexEntry.compression_ratio` can divide by zero for empty sections. Section names are limited to letters, digits, slash, and hyphen. Atomic rename is local-filesystem safe but still depends on directory fsync semantics not represented here. Unsupported checksum methods fail at read time.

## Test signals
Tests should cover v1/v2 magic detection, unsupported versions, bad magic, bounded reads, compressed seeking at flush boundaries, index load failures after recompression, section size mismatch, checksum mismatch, section full-read enforcement, atomic rename and temp cleanup on failure, duplicate/nested/invalid section names, deterministic gzip mtime, JSON/blob/table round trips, and network-order assignment compatibility.
