## sources/distributed-fs/xrootd/src/XrdEc/XrdEcObjCfg.hh

### Purpose
This header defines `XrdEc::ObjCfg`, the immutable layout and placement description for one erasure-coded object, plus the selected checksum implementation.

### Important APIs, Types, and Functions
- `isal_crc32` wraps ISA-L `crc32_gzip_refl`.
- `ObjCfg` constructor accepts object id/path, data stripe count, parity count, chunk size, checksum selection, and optional no-metadata-file mode.
- Derived constants include `nbchunks`, `datasize`, `paritysize`, and `blksize`.
- `GetDataUrl(i)` and `GetMetadataUrl(i)` build placement URLs with optional CGI strings.
- `GetFileName(blknb, strpnb)` names zip entries as `obj.<block>.<stripe>`.
- `digest` points to either XRootD crc32c or ISA-L crc32.

### Control Flow
`ObjCfg` is constructed by the EC handler after URL parameters are parsed. Placements and CGI vectors are filled afterward by the caller. Reader and writer code use the object to map logical offsets to block/stripe file names and remote data/metadata URLs.

### State and Persistence
Most layout fields are `const`, while placement vectors and CGI vectors are mutable configuration populated after construction. It does not own remote state, but its naming scheme determines the persistent zip-entry names and metadata object names.

### Dependencies and Integration Points
Depends on XrdOuc CRC32C and ISA-L CRC APIs. Used by `Reader`, `StrmWriter`, `WrtBuff`, `RedundancyProvider`, `Config`, and XrdCl EC handler code.

### Risks and Edge Cases
`nbdata + nbparity` is stored as `uint8_t`; invalid large counts can wrap if not validated before construction. URL getters assume placement and CGI vectors contain an entry for index `i`. `blksize` comment says MB but value is bytes. `digest` is a raw function pointer and must be valid for object lifetime.

### Test Signals
Tests should cover layout arithmetic, URL generation with and without CGI, metadata URL suffixing, file-name format, digest selection, and invalid placement-index behavior at the EC handler validation layer.
