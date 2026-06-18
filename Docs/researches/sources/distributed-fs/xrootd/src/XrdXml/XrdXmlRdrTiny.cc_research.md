# sources/distributed-fs/xrootd/src/XrdXml/XrdXmlRdrTiny.cc

## Purpose

This file implements `XrdXmlReader` using the bundled TinyXML DOM parser. It gives XRootD a small in-process XML reader suitable for small documents such as Metalink files.

## Important APIs, Types, and Functions

- `XrdXmlRdrTiny::XrdXmlRdrTiny(bool &aOK, const char *fname, const char *enc)`: validates the file with `stat`, loads it into a `TiXmlDocument`, initializes traversal pointers, and reports construction success.
- `GetElement(const char **ename, bool reqd)`: searches sibling/child DOM nodes for named elements inside a caller-specified scope.
- `GetAttributes(const char **aname, char **aval)`: duplicates matching attribute values from the current element using `strdup`.
- `GetText(const char *ename, bool reqd)`: duplicates simple text from the current element via `TiXmlElement::GetText`.
- `Init()`: always returns true.

## Control Flow

Construction loads the entire XML document into memory, stores the document as the initial `curNode`, and sets `elmNode` to the current scan point. `GetElement` verifies the requested scope against the current node or last returned element, chooses the next child or sibling scan start, and returns the index of the first requested element. When no matching element remains in the scope, it moves back to the parent and returns 0. `GetAttributes` and `GetText` require a successful prior `GetElement`.

## State and Persistence Behavior

The reader owns a `TiXmlDocument *reader` and deletes it in the destructor. Traversal state is held in `curNode`, `curElem`, and `elmNode`. Error state is stored as `eCode` and `eText`; debug printing to `stderr` is enabled by `XrdXmlDEBUG`.

## Dependencies and Integration Points

The implementation depends on bundled `tinyxml.h`, POSIX `stat`, `XrdSysE2T`, and the abstract `XrdXmlReader` contract. It is the default implementation selected by `XrdXmlReader::GetReader` and is used by `XrdXmlMetaLink` unless another implementation is requested.

## Risks

- The `reqd` error block in `GetElement` is unreachable because the function returns 0 before checking `reqd`; required missing elements may not set the intended error.
- It builds a full DOM tree, so large XML inputs consume memory and parsing time upfront.
- The `enc` constructor argument is ignored, leaving TinyXML to auto-detect or parse under defaults.
- Only simple first-child text is returned by `TiXmlElement::GetText`; mixed-content XML can be truncated.
- Error handling around `LoadFile` appears inverted for `ErrorDesc()` emptiness and may report "Unknown error" in some parser-error cases.

## Test Signals

Tests should cover required and optional element misses, nested scope transitions, repeated sibling scans, attribute duplication/freeing, mixed-content text behavior, invalid XML load errors, `XrdXmlDEBUG` trace output, and large document rejection expectations at a higher layer.
