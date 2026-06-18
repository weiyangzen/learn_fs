# sources/distributed-fs/xrootd/src/XrdZip/XrdZipLFH.hh

## Purpose

`sources/distributed-fs/xrootd/src/XrdZip/XrdZipLFH.hh` defines the Local File Header representation for XRootD ZIP support. It creates, parses, and serializes the per-file header that precedes file data, including ZIP64 extra metadata for large files. The source was read as a complete 178-line file.

## Important APIs, Types, and Functions

`struct LFH` provides static `initSize()` to choose a 32-bit size or overflow sentinel, a writing constructor from filename, CRC, file size, and timestamp, a parsing constructor from a buffer and optional size bound, `Serialize()`, and `ParseExtra()`. Fields include `minZipVersion`, `generalBitFlag`, `compressionMethod`, DOS timestamp, CRC32, compressed and uncompressed size, filename and extra lengths, filename, optional `Extra`, and computed `lfhSize`. Constants are `lfhSign = 0x04034b50` and `lfhBaseSize = 30`.

## Control Flow

Writing construction initializes a stored method entry, sets both compressed and uncompressed sizes to the input file size or the 32-bit overflow sentinel, creates an `Extra`, selects minimum ZIP version 10 or 45 depending on ZIP64 use, and computes header size. Parsing validates the signature, reads fixed fields with `from_buffer()`, checks variable-field bounds when `bufferSize` is supplied, copies the filename, and parses ZIP64 extra data only when 32-bit sizes are overflow sentinels. Serialization writes fixed fields, filename, and serialized extra data in order.

## State and Persistence Behavior

`LFH` holds an in-memory copy of persistent ZIP local-header metadata. The serialized state is written before file data in the archive. It owns filename and optional ZIP64 `Extra` data; file data itself is not represented here.

## Dependencies and Integration Points

The header includes `XrdZipUtils.hh`, `XrdZipExtra.hh`, and STL string/memory/algorithm helpers. It integrates with `CDFH` construction, archive file entry writing, ZIP64 extra parsing, DOS timestamp conversion, and code that locates file data after the local header.

## Risks and Edge Cases

The parser is bounded only when `bufferSize` is nonzero; default construction from an untrusted pointer requires prior validation. If overflowed sizes require a ZIP64 extra but `Extra::Find()` returns null, `extra` remains a default object with zero sizes, which may hide malformed archives until later size use. Filename length is stored as `uint16_t`; constructing from a longer `std::string` would truncate length semantics. The code assumes stored/no-compression entries because compressed and uncompressed sizes are initialized identically.

## Test Signals

Tests should cover small-file construction, ZIP64-size construction, serialization round trips, parsing invalid signatures, truncated fixed headers, truncated filename and extra data with bounds, missing ZIP64 extra when size sentinels are present, multiple extra records, zero-length filenames if allowed by caller policy, maximum 16-bit filename/extra lengths, and compatibility with `CDFH(LFH*, mode, offset)`.
