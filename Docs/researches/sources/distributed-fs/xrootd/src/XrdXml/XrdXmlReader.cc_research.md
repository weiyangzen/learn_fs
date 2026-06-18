# sources/distributed-fs/xrootd/src/XrdXml/XrdXmlReader.cc

## Purpose

This file implements the factory and preinitialization methods for the abstract XML reader interface.

## Important APIs, Types, and Functions

- `XrdXmlReader::GetReader(const char *fname, const char *enc, const char *impl)`: creates either `XrdXmlRdrTiny` or, when compiled in, `XrdXmlRdrXml2`.
- `XrdXmlReader::Init(const char *impl)`: returns true for TinyXML and delegates to `XrdXmlRdrXml2::Init` for libxml2.

## Control Flow

If `impl` is null or `"tinyxml"`, the factory constructs a TinyXML reader and returns it on successful construction. If construction fails, it fetches the reader error code, deletes the reader, sets `errno`, and returns null. If `impl` is `"libxml2"` and `HAVE_XML2` is available, the same pattern is used for `XrdXmlRdrXml2`. Unknown or unavailable implementations set `errno=ENOTSUP`.

## State and Persistence Behavior

The file keeps no persistent state. Ownership of a successful reader transfers to the caller, who must delete it. Failure diagnostics are reported through `errno` after the temporary object is deleted.

## Dependencies and Integration Points

It always includes `XrdXmlRdrTiny.hh` and conditionally includes `XrdXmlRdrXml2.hh`. `HAVE_XML2` is defined by `src/XrdXml/CMakeLists.txt`. `XrdXmlMetaLink` and any other XML consumers use this file as the implementation-selection point.

## Risks

- Implementation selection is stringly typed and silently defaults null to TinyXML.
- Error text from failed constructors is lost after deletion; callers only receive `errno`.
- No plugin or registry mechanism exists; adding readers requires editing this factory.

## Test Signals

Tests should validate null, `"tinyxml"`, `"libxml2"`, and unknown implementation strings; `errno` on nonexistent files; `Init` behavior in both build modes; and ownership cleanup of returned reader objects.
