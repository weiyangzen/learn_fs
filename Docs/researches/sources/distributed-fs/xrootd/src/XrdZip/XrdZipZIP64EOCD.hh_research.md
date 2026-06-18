# sources/distributed-fs/xrootd/src/XrdZip/XrdZipZIP64EOCD.hh

Purpose: Models the ZIP64 End of Central Directory record. It supports parsing from a raw central-directory trailer and constructing/serializing a new ZIP64 EOCD for archives whose central directory offsets, sizes, or counts exceed ZIP32 limits.

Important APIs/types/functions: `ZIP64_EOCD(const char*)` reads fixed offsets for record size, ZIP versions, disk numbers, entry counts, central-directory size, and central-directory offset. `ZIP64_EOCD(uint64_t cdoff, uint32_t cdcnt, uint32_t cdsize)` builds a single-disk ZIP64 record with version-made-by `(3 << 8) | 63` and minimum version `45`. `Serialize(buffer_t&)` appends the signature and fields in ZIP order. `ToString()` exposes fields for logging. Constants include `zip64EocdSign` and `zip64EocdBaseSize`.

Control flow: Parsing is offset-based and delegates endian conversion to `XrdZipUtils::to`. Construction fills single-disk fields and calculates `zip64EocdSize` as total base size plus extensible data minus the 12 bytes excluded by the ZIP spec. Serialization writes the signature, scalar fields, and optional `extensibleData`.

State and persistence behavior: The struct stores all ZIP64 EOCD fields as public members. Serialized state is persisted into a ZIP trailer; no external resource state is managed.

Dependencies and integration points: Includes ZIP utility functions and related LFH/CDFH headers. It integrates with ZIP writer/reader code that needs a ZIP64 trailer and with `ZIP64_EOCDL`, which points to this record.

Risks: The parsing constructor ignores the actual extensible data length and initializes `extensibleDataLength` to zero even though `zip64EocdSize` could indicate extra bytes. It also does no signature or length validation. `ToString()` writes `std::string extensibleData` directly, which can contain binary data.

Test signals: Tests should cover parsing known ZIP64 trailers, serialization byte-for-byte output, archives with no extensible data, and callers rejecting buffers with wrong signatures or insufficient length.
