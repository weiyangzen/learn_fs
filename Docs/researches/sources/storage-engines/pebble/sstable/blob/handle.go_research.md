# sources/storage-engines/pebble/sstable/blob/handle.go

## Purpose
This file defines blob value handle types and fast varint encoding/decoding used inside SSTable values and blob retrieval paths.

## Important APIs, Types, and Functions
`MaxInlineHandleLength` bounds encoded inline handles.

`BlockValueID`, `BlockID`, and `Handle` identify a value within a blob file. `Handle` string formatting is redact-safe.

`InlineHandlePreface` stores the SSTable-local blob reference ID and value length. `HandleSuffix` stores block ID and value ID. `InlineHandle` combines both.

`HandleSuffix.Encode` and `InlineHandle.Encode` varint-encode fields.

`DecodeInlineHandlePreface` decodes reference ID and value length with manually inlined unsafe uvarint logic.

`DecodeHandleSuffix` decodes block ID and value ID with manually inlined unsafe uvarint logic.

## Control Flow
Encoding uses `binary.PutUvarint`. Decoding reads up to five bytes per uint32 field with unrolled branches, updating the remaining source slice for preface decoding and an unsafe pointer for suffix decoding.

## State and Persistence Behavior
Inline handles are persisted within SSTable value blocks, referring indirectly to blob files through the containing table's blob references. Full `Handle` values are runtime descriptions that include the resolved blob file ID.

## Dependencies and Integration Points
The code integrates with `base.BlobFileID`, `base.BlobReferenceID`, redact-safe formatting, and `ValueFetcher.FetchHandle`. It is exercised by blob writer/fetcher tests and by SSTable code that returns `InternalValue`s.

## Risks
Unsafe decoders assume the source buffer is well-formed and long enough for encoded fields; malformed inputs can panic or read out of bounds if not validated by higher layers. Manual decoding must stay semantically equivalent to uvarint encoding. Maximum length assumes four 32-bit varints.

## Test Signals
`TestHandleRoundtrip` in `blob_test.go` validates representative inline handle encode/decode round trips.
