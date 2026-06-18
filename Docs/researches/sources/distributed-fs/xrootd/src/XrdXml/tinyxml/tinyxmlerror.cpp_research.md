# sources/distributed-fs/xrootd/src/XrdXml/tinyxml/tinyxmlerror.cpp

## Purpose

This file defines TinyXML's static English error-message table.

## Important APIs, Types, and Functions

- `TiXmlBase::errorString[TIXML_ERROR_STRING_COUNT]`: maps TinyXML error IDs to user-facing text.

## Control Flow

There is no executable control flow beyond static initialization. Parser and document code call `TiXmlDocument::SetError`, which indexes this array through the `TiXmlBase` error enum.

## State and Persistence Behavior

The table is process-static read-only text. It does not persist state between parses beyond being globally available.

## Dependencies and Integration Points

It includes `tinyxml.h` for enum definitions. The split file is intended to make future localization easier and keep messages out of parser implementation files.

## Risks

- Messages are English-only.
- The array must stay in exact enum order; adding/removing error IDs without updating this file will misreport errors or fail compilation.
- Some messages are generic, so higher-level callers may need filename/context from other state.

## Test Signals

Tests should trigger each parse error ID and verify `ErrorDesc()` returns the expected non-null text. Compile-time checks should catch mismatch with `TIXML_ERROR_STRING_COUNT`.
