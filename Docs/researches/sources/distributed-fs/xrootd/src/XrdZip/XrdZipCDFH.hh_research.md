# sources/distributed-fs/xrootd/src/XrdZip/XrdZipCDFH.hh

## Purpose

`sources/distributed-fs/xrootd/src/XrdZip/XrdZipCDFH.hh` defines the Central Directory File Header representation for XRootD ZIP support. It parses, stores, serializes, and indexes ZIP central-directory entries, including ZIP64 extra fields for overflowed sizes, offsets, and disk numbers. The source was read as a complete 357-line file.

## Important APIs, Types, and Functions

The namespace exports `struct CDFH`, `cdvec_t` as `std::vector<std::unique_ptr<CDFH>>`, `cdmap_t` as filename-to-index map, and `cdrecs_t` as filename-to-record map. Static `Parse()` overloads read fixed-count or signature-delimited central directory records. `CalcSize()` and static `Serialize()` combine existing original central-directory bytes with appended records. Constructors build a CDFH from an `LFH` plus mode and offset, or parse one from a buffer. `GetOffset()` chooses the 32-bit header offset or ZIP64 extra offset. `ParseExtra()` locates and decodes ZIP64 data. Instance `Serialize()`, `IsZIP64()`, and `HasDataDescriptor()` expose serialization and feature checks.

## Control Flow

Fixed-count parsing walks `nbCdRecords`, validates the central-directory signature, constructs a `CDFH` with a maximum remaining buffer size, advances by `cdfhSize`, and records filename-to-index mappings. Signature-delimited parsing stops when the next signature is not a CDFH signature, leaving the caller's buffer pointer at the first non-CDFH record. Serialization writes fields in ZIP order, then filename, optional extra, and optional comment. Construction from an LFH mirrors file metadata and creates a central-directory ZIP64 extra if the local-header extra or local-header offset requires it.

## State and Persistence Behavior

`CDFH` is an in-memory representation of archive metadata. Persistent state is the serialized central-directory record written into a ZIP archive. Parsed records own `filename`, `comment`, and an optional `Extra`. ZIP64 values are stored in `extra` when 32-bit fields are overflow sentinels.

## Dependencies and Integration Points

The header includes `XrdZipLFH.hh`, `XrdZipUtils.hh`, and `XrdZipDataDescriptor.hh`, plus STL containers and `sys/types.h`. It integrates with local file headers, data descriptor flags, ZIP64 extra parsing, archive central-directory indexing, and any XRootD ZIP reader/writer code that appends files or looks up entries by name.

## Risks and Edge Cases

The fixed-count `Parse()` checks `bufferSize < cdfhBaseSize` without accounting for the current `offset`, then reads `buffer + offset`; this is safe only because `bufferSize` is decremented in parallel, but it is easy to break if modified. The buffer constructor validates total record size only when `maxSize > 0`; callers using the default must already guarantee enough bytes for variable fields. `ParseExtra()` silently leaves `extra` null if overflow fields require ZIP64 data but the extra record is absent, so later `GetOffset()` on an overflowed offset assumes valid `extra`. Filename duplicate handling overwrites the map entry while retaining both vector entries.

## Test Signals

Tests should parse central directories with zero, one, and many records; truncated fixed fields; truncated filename/extra/comment; invalid signatures; duplicate filenames; ZIP64 compressed size, uncompressed size, offset, and disk overflow combinations; data-descriptor flag detection; appended serialization after an original central directory; and round-trip serialization for LFH-derived and parsed records.
