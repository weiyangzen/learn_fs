# sources/distributed-fs/xrootd/src/XrdXml/XrdXmlReader.hh

## Purpose

This header defines the abstract pull-style XML reader API used by XRootD XML consumers. It hides TinyXML and libxml2 behind a small common interface.

## Important APIs, Types, and Functions

- Pure virtual `GetAttributes`, `GetElement`, `GetError`, and `GetText`.
- Static `GetReader` factory, with implementation choices `"tinyxml"` and `"libxml2"`.
- Static `Init`, intended for preinitializing implementations with global/thread-safety requirements.

## Control Flow

Callers obtain a reader for a file, repeatedly call `GetElement` with a scope-plus-candidates array, then call `GetAttributes` and/or `GetText` for the current tag. `GetElement` returns 0 on scope end or not found, and positive indexes corresponding to the candidate array.

## State and Persistence Behavior

The base class has no state and a virtual destructor. State, memory allocation strategy, and parser cursor behavior are implementation-specific. The API specifies that returned attribute values and text must be freed with `free()`.

## Dependencies and Integration Points

The header is intentionally dependency-light and is consumed by `XrdXmlMetaLink`, `XrdXmlRdrTiny`, `XrdXmlRdrXml2`, and factory callers. It documents that TinyXML builds a full DOM and libxml2 streams.

## Risks

- The API overloads return value 0 for scope end and not-found, so callers must inspect `GetError` when required semantics matter.
- Memory ownership is C-style and relies on callers freeing every returned string.
- The comments contain small typos and say `GetRead()` rather than `GetReader()`, but the API itself is clear.
- Implementation-specific thread-safety is exposed only through documentation, not type constraints.

## Test Signals

Contract tests should run the same XML traversal through both implementations where available, verify string-free ownership, confirm required-tag error behavior, and test threaded preinitialization guidance for libxml2.
