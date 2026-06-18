# sources/distributed-fs/xrootd/src/XrdXml/XrdXmlMetaLink.hh

## Purpose

This header declares the Metalink conversion interface that turns XML specifications into `XrdOucFileInfo` objects. It documents that conversion is intentionally permissive and may accept non-strict Metalink v3/v4 inputs when enough usable information is present.

## Important APIs, Types, and Functions

- `XrdXmlMetaLink::Convert`: returns one `XrdOucFileInfo` for the first usable file entry.
- `XrdXmlMetaLink::ConvertAll`: returns all usable file entries plus a count.
- `XrdXmlMetaLink::DeleteAll`: companion cleanup helper for `ConvertAll`.
- `GetStatus(int &ecode)`: exposes `eText` and `eCode` from the previous conversion.
- Constructor parameters: `protos` URL protocol allow-list, `rdprot` synthetic global-file protocol, `rdhost` synthetic global-file host, and `encode` XML encoding hint.

## Control Flow

The public methods delegate to private parser helpers. The class owns its current `XrdXmlReader`, active and linked `XrdOucFileInfo` instances, protocol strings, temporary filename buffer, and status text. The constructor duplicates `protos` and `encode`, stores redirect parameters by pointer, initializes counters and flags, and clears error/temp buffers.

## State and Persistence Behavior

Per-object state is mutable across conversions. `prots` and `encType` are heap-duplicated and freed in the destructor. `rdProt` and `rdHost` are borrowed pointers, so callers must ensure their lifetime covers the converter use. `tmpFn` and `eText` are fixed-size buffers.

## Dependencies and Integration Points

The header depends on `XrdOucFileInfo.hh` and `XrdXmlReader.hh`. It exposes the expected ownership model: returned file info objects are owned by the caller, and arrays from `ConvertAll` require deleting each element or calling `DeleteAll`.

## Risks

- Borrowed `rdProt` and `rdHost` can dangle if caller-provided storage is transient.
- The destructor does not delete any active `reader` or file list; implementation relies on conversion-time RAII cleanup and caller ownership transfers.
- Fixed-size error buffers truncate long filesystem or parser messages.
- Stateful members make object reuse sensitive to flags such as `doAll` and prior errors.

## Test Signals

Header-level contract tests should verify default constructor behavior (`root:xroot:` filter and `xroot:` redirect protocol), caller ownership of returned objects, `GetStatus` after success and failure, and safe destruction after failed conversions.
