# sources/distributed-fs/xrootd/src/XrdXml/tinyxml/tinyxml.cpp

## Purpose

This file implements most TinyXML DOM operations, printing, file loading/saving, attribute handling, cloning, visitor traversal, and in-memory XML string generation.

## Important APIs, Types, and Functions

- `TiXmlBase::EncodeString`: escapes XML special characters and control bytes.
- `TiXmlNode` operations: construction/destruction, child insertion/replacement/removal, sibling/child traversal, `GetDocument`.
- `TiXmlElement`: attribute getters/setters/query methods, `Print`, `CopyTo`, `Accept`, `Clone`, and `GetText`.
- `TiXmlDocument`: `LoadFile`, `SaveFile`, `Parse` entry support, error state copying, `Print`, `Accept`, and cloning.
- `TiXmlAttribute`, `TiXmlAttributeSet`: query/print/set numeric values and manage circular attribute lists.
- `TiXmlHandle`: null-safe child traversal wrapper.
- `TiXmlPrinter`: visitor that prints XML to a buffer with configurable indentation and line breaks.

## Control Flow

DOM nodes own linked lists of children; insert operations clone or link nodes and wire `parent`, `prev`, and `next` pointers. Destructors recursively delete children, and element cleanup deletes attributes. `LoadFile` reads the whole file in binary mode, normalizes CR/LF sequences in memory, calls `Parse`, and returns whether the document has an error. Printing walks the DOM recursively or via the visitor and emits compact or formatted XML depending on node shape.

## State and Persistence Behavior

Documents persist an in-memory DOM, error flags, row/column location, tab size, and UTF-8 BOM state. Nodes persist value strings, user data pointers, source locations, parent/child/sibling pointers, and type tags. File load/save persists XML to disk only when callers invoke document file methods. Static state includes whitespace condensation in `TiXmlBase::condenseWhiteSpace`.

## Dependencies and Integration Points

It depends on `tinyxml.h`, C `FILE *` I/O, and optional STL stream support. In this repository it is bundled into `XrdTinyXml` and consumed by `XrdXmlRdrTiny` for DOM parsing.

## Risks

- Loading reads entire files into memory and uses `long` file lengths from `ftell`, which is unsuitable for very large files.
- The DOM owns linked raw pointers; misuse of `LinkEndChild` ownership can cause leaks or double deletes outside expected patterns.
- Printing uses `fprintf` and buffers, so malformed values are escaped only through paths that call `EncodeString`.
- `TiXmlPrinter` uses a single `simpleTextPrint` bool, which can be fragile for nested visitor state.
- Error reporting stores only the first error and uses English static strings.

## Test Signals

Tests should cover parse/load/save round trips, CR/LF normalization, element/attribute mutation, cloning, child replacement/removal, visitor printing, CDATA/text/comment/declaration/unknown nodes, duplicate document-child rejection, and memory-sanitizer runs for ownership operations.
