# sources/distributed-fs/xrootd/src/XrdZip/XrdZipZIP64EOCDL.hh

Purpose: Models the ZIP64 End of Central Directory Locator, the fixed-size record that tells ZIP readers where the ZIP64 EOCD record is located.

Important APIs/types/functions: `ZIP64_EOCDL(const char*)` parses disk number, ZIP64 EOCD offset, and disk count from a raw buffer. `ZIP64_EOCDL(const EOCD&, const ZIP64_EOCD&)` computes the ZIP64 EOCD record offset from the normal EOCD fields when possible, falling back to ZIP64 central-directory offset and size when the ZIP32 fields contain overflow sentinels. `Serialize(buffer_t&)` emits the locator signature and fields. `ToString()` provides log-friendly formatting. Constants are `zip64EocdlSign` and `zip64EocdlSize`.

Control flow: The construction-from-records path starts with a zero disk number and one total disk, chooses the central directory offset from EOCD or ZIP64 EOCD, then adds central directory size from EOCD or ZIP64 EOCD to land at the ZIP64 EOCD position.

State and persistence behavior: The struct stores only the locator fields and serializes them into the ZIP trailer. There is no dynamic ownership or cache state.

Dependencies and integration points: Depends on `EOCD`, `ZIP64_EOCD`, and `ovrflw<uint32_t>` to recognize ZIP32 overflow. It is written after the ZIP64 EOCD and before the classic EOCD in ZIP64 archives.

Risks: Parsing does not validate signature or buffer length. The computed offset assumes a single-disk archive and specific central-directory layout. Multi-disk ZIP64 archives are represented by fields but not truly supported by the constructor.

Test signals: Important tests include locator serialization size/signature, offset computation when EOCD fields are normal, offset computation when EOCD fields overflow, and rejection of malformed buffers at higher-level callers.
