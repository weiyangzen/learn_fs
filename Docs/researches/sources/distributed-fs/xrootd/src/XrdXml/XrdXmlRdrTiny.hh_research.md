# sources/distributed-fs/xrootd/src/XrdXml/XrdXmlRdrTiny.hh

## Purpose

This header declares the TinyXML-backed implementation of the abstract `XrdXmlReader` interface.

## Important APIs, Types, and Functions

- Overrides `GetAttributes`, `GetElement`, `GetError`, and `GetText`.
- `static bool Init()`: preinitialization hook, currently trivial.
- Constructor and destructor manage an underlying `TiXmlDocument`.
- Private `Debug` emits traversal diagnostics when enabled.

## Control Flow

The class exposes the same pull-style reader interface as other implementations: callers fetch an element, then fetch attributes or text from the current element. Internally, the `.cc` file uses DOM node pointers to emulate a streaming-ish scoped walk.

## State and Persistence Behavior

Persistent per-reader fields include the TinyXML document pointer, current node/element pointers, last error code/text, and a debug flag. The fixed `eText[251]` buffer stores transient error descriptions.

## Dependencies and Integration Points

The header forward-declares `TiXmlDocument`, `TiXmlElement`, and `TiXmlNode` to avoid exposing TinyXML internals to users. It inherits from `XrdXmlReader` and is instantiated by `XrdXmlReader::GetReader`.

## Risks

- The file comment says "based on libxml2" even though this is the TinyXML reader, which can mislead maintainers.
- Traversal state is mutable and not thread-safe per instance.
- Error buffer size is fixed and may truncate.

## Test Signals

Compile tests should validate no TinyXML header leak through this header. Behavioral tests should instantiate through `XrdXmlReader::GetReader` and verify virtual dispatch through the abstract interface.
