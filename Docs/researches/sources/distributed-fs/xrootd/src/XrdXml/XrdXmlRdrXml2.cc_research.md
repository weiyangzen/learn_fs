# sources/distributed-fs/xrootd/src/XrdXml/XrdXmlRdrXml2.cc

## Purpose

This file implements the optional libxml2-backed `XrdXmlReader`. It provides a streaming XML reader better suited to larger documents and exposes the same element, attribute, text, and error methods as the TinyXML adapter.

## Important APIs, Types, and Functions

- `XrdXmlRdrXml2::XrdXmlRdrXml2(bool &aOK, const char *fname, const char *enc)`: creates an `xmlTextReader` for a file path.
- `GetElement(const char **ename, bool reqd)`: advances the libxml2 reader until one of the requested start tags is found or the current scope end tag is reached.
- `GetAttributes(const char **aname, char **aval)`: iterates attributes on the current start element, duplicates requested values, and returns whether any were found.
- `GetText(const char *ename, bool reqd)`: reads the next node and returns text content if present.
- `Init()`: calls `xmlInitParser`.
- `Free(void *strP)`: wrapper for `xmlFree`, though the public base class does not declare it.

## Control Flow

Construction stores a duplicated encoding string in `encType`, initializes flags, and opens the libxml2 text reader. `GetElement` calls `xmlTextReaderRead` in a loop, skips significant whitespace or nameless nodes, returns the requested element index on a matching start element, and stops when it sees the caller-provided scope end element. Attribute and text methods operate relative to the current libxml2 cursor.

## State and Persistence Behavior

The instance owns `_xmlTextReader *reader` and frees it in the destructor. It also stores `encType`, `eCode/eText`, `doDup`, and a debug flag. Returned strings are duplicated with `strdup` by default so callers can use `free()` consistently, avoiding libxml allocator ownership leakage.

## Dependencies and Integration Points

The implementation depends on `<libxml/xmlreader.h>`, `XrdSysE2T`, and `XrdXmlReader`. It is compiled only when `HAVE_XML2` is defined by CMake and selected by `XrdXmlReader::GetReader(..., "libxml2")`.

## Risks

- `encType` is allocated but not freed in the destructor, producing a small per-reader leak when an encoding is supplied.
- The constructor ignores `encType` when calling `xmlNewTextReaderFilename`, so the encoding hint is effectively unused.
- `GetAttributes` leaves the reader positioned on the last attribute, relying on later libxml2 reads to recover correctly.
- `GetText` only checks the immediate next node for text, so mixed content or CDATA can be missed.
- libxml2 global initialization requirements are documented at the base layer; callers must invoke `Init("libxml2")` early in threaded applications.

## Test Signals

Tests should build with LibXml2 enabled, call `Init("libxml2")`, parse large documents without full-DOM memory spikes, verify scope-end behavior, exercise missing required elements, attribute duplication/freeing, CDATA/text handling, and run under leak checking for encoded reader creation.
