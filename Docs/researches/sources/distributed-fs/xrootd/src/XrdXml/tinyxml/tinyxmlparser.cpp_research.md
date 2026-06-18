# sources/distributed-fs/xrootd/src/XrdXml/tinyxml/tinyxmlparser.cpp

## Purpose

This file implements TinyXML's tokenizer and parser: entity decoding, UTF-8 handling, whitespace skipping, document parsing, node identification, element/attribute/text/comment/declaration parsing, and optional STL stream ingestion.

## Important APIs, Types, and Functions

- Static parser data: `TiXmlBase::entity`, UTF-8 BOM constants, and `TiXmlBase::utf8ByteTable`.
- Encoding helpers: `ConvertUTF32ToUTF8`, `IsAlpha`, `IsAlphaNum`, `SkipWhiteSpace`, `ReadName`, `GetEntity`, `StringEqual`, `ReadText`.
- `TiXmlParsingData::Stamp`: maintains source row/column location.
- Parse methods: `TiXmlDocument::Parse`, `TiXmlElement::Parse`, `TiXmlElement::ReadValue`, `TiXmlUnknown::Parse`, `TiXmlComment::Parse`, `TiXmlAttribute::Parse`, `TiXmlText::Parse`, and `TiXmlDeclaration::Parse`.
- `TiXmlNode::Identify`: selects concrete node type from the next XML prefix.

## Control Flow

Parsing starts at `TiXmlDocument::Parse`, which initializes encoding and location state, skips whitespace, identifies nodes, parses them, links them into the document, and updates encoding after an XML declaration. Elements parse a start tag, attributes, empty-tag endings, nested content through `ReadValue`, and matching end tags. Text parsing reads until `<`, CDATA reads until `]]>`, comments read until `-->`, and attributes parse quoted or lenient unquoted values with entity expansion.

## State and Persistence Behavior

The parser mutates DOM node values, child lists, attributes, document error state, parse locations, and document encoding/BOM state. It does not persist outside memory except through later save/print calls.

## Dependencies and Integration Points

It depends on `tinyxml.h`, C string utilities, and optional STL stream support. In XRootD, it is exercised indirectly by `XrdXmlRdrTiny::LoadFile` and therefore by Metalink conversion.

## Risks

- The parser is intentionally lenient in places, including unquoted attributes, and does not provide full XML validation.
- Non-ASCII name handling is approximate: bytes above ASCII are treated generously as letters.
- Entity parsing accepts only built-ins plus numeric references; unknown entities are passed through imperfectly.
- Recursive DOM parsing can consume significant memory and stack for deeply nested inputs.
- Encoding support is limited to UTF-8 versus legacy heuristics.

## Test Signals

Tests should cover UTF-8 BOM handling, numeric and built-in entities, invalid entities, whitespace condensation toggles, duplicate attributes, unclosed elements, mismatched end tags, CDATA, comments containing entity-like text, declarations with encoding, row/column errors, and deeply nested or malformed XML.
