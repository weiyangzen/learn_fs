# sources/distributed-fs/xrootd/src/XrdXml/XrdXmlRdrXml2.hh

## Purpose

This header declares the optional libxml2 implementation of `XrdXmlReader`.

## Important APIs, Types, and Functions

- Overrides `GetAttributes`, `GetElement`, `GetError`, and `GetText`.
- Adds `Free(void *strP)` for libxml-allocated string cleanup, although current implementation normally duplicates values with `strdup`.
- `static bool Init()` exposes libxml2 preinitialization.
- Private helpers `Debug` and `GetName` wrap diagnostic output and libxml name extraction.

## Control Flow

The class is instantiated by `XrdXmlReader::GetReader` when the implementation string is `"libxml2"` and the build includes `HAVE_XML2`. Users interact only through the base pull-reader interface.

## State and Persistence Behavior

It stores a libxml2 text reader pointer, borrowed/duplicated encoding text, an error buffer, a duplication mode flag, and debug mode. The reader object is mutable and intended for one parsing stream.

## Dependencies and Integration Points

The header forward-declares `_xmlTextReader` to avoid exposing libxml2 headers. It depends on `XrdXmlReader.hh` and is included only when CMake finds LibXml2.

## Risks

- `Free` is not present in the base class, so generic callers cannot rely on it through `XrdXmlReader *`.
- The implementation is not always available; code must handle `ENOTSUP` in non-libxml2 builds.
- Per-instance use is not thread-safe, and libxml2 global state requires preinitialization in threaded programs.

## Test Signals

Compile tests should cover LibXml2-present and LibXml2-absent builds. Interface tests should confirm selecting `"libxml2"` returns this implementation only when compiled in and that all returned strings can be released with `free()` under default duplication mode.
