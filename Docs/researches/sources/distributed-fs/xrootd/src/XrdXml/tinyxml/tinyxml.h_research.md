# sources/distributed-fs/xrootd/src/XrdXml/tinyxml/tinyxml.h

## Purpose

This header declares the TinyXML 2.6.2 DOM, parser, visitor, handle, printer, encoding, and error APIs vendored into XRootD.

## Important APIs, Types, and Functions

- Version constants `TIXML_MAJOR_VERSION`, `TIXML_MINOR_VERSION`, `TIXML_PATCH_VERSION`.
- `TiXmlBase`: common parse helpers, error IDs, entity helpers, encoding helpers, whitespace policy, row/column/user data.
- `TiXmlNode`: parent/child/sibling DOM base with virtual `Parse`, `Clone`, `Print`, `Accept`, and cast helpers.
- `TiXmlElement`, `TiXmlAttribute`, `TiXmlAttributeSet`: elements and attributes, including typed query helpers.
- `TiXmlText`, `TiXmlComment`, `TiXmlDeclaration`, `TiXmlUnknown`, and `TiXmlDocument`: concrete XML node types.
- `TiXmlVisitor`, `TiXmlHandle`, and `TiXmlPrinter`: visitor traversal, null-safe navigation, and string printing.

## Control Flow

The header defines a classic object-oriented DOM. Parsing starts at `TiXmlDocument::Parse` or `LoadFile`, which creates concrete node objects through virtual parse methods. Navigation uses child/sibling linked lists. Output uses recursive `Print` or visitor-based `Accept` through `TiXmlPrinter`.

## State and Persistence Behavior

Every node stores value, parent/child/sibling pointers, type, user data, and parse location. Documents add error state, tab size, and BOM flag. Attribute sets use a circular sentinel list. Static parser state includes entity tables, UTF-8 byte table, error strings, and whitespace condensation.

## Dependencies and Integration Points

The header can use STL strings/streams when `TIXML_USE_STL` is set; otherwise it depends on `tinystr.h`. XRootD's TinyXML reader includes this header directly and uses `TiXmlDocument`, `TiXmlNode`, and `TiXmlElement`.

## Risks

- The API predates modern C++ ownership conventions and uses raw pointers extensively.
- Non-STL mode supplies only a partial string implementation.
- XML namespace, DTD, schema, streaming, and full encoding support are limited.
- Many methods return null on error without rich diagnostics unless the containing document has error state.

## Test Signals

Header/API tests should compile both STL and non-STL modes, exercise public DOM navigation and mutation APIs, verify error IDs and row/column reporting, and ensure XRootD's `XrdXmlRdrTiny` only relies on stable public APIs.
