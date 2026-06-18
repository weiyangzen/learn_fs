# sources/storage-engines/pebble/sstable/test_utils.go

## Purpose
Provides test helpers for reading full SSTable contents, parsing textual key/span specifications, constructing SSTables from test input, and parsing writer options for datadriven tests.

## Important APIs, Types, And Functions
`ReadAll` returns point KVs, range deletions, and range keys. `ParsedKVOrSpan` models point keys, range spans, blob handles, dual-tier blob handles, and force-obsolete markers. `ParseTestKVsAndSpans`, `ParseTestSST`, `ParseWriterOptions`, `testingBloomFilterPolicy`, `makeTestingBloomFilterPolicy`, and `comparerFromCmdArg` are the main utilities.

## Control Flow
Parsing walks line-oriented input, handles `Span:` lines through `keyspan.ParseSpan`, point lines through `base.ParseInternalKV`, optional `force-obsolete`, blob/dual-tier handle decoding, attributes, and test-key metadata extraction. `ParseTestSST` dispatches each parsed item to `RawWriter.Add`, blob add methods, or `EncodeSpan`. Writer option parsing mutates `WriterOptions` from datadriven command args.

## State And Persistence Behavior
Helpers create or read SSTable state through supplied readers/writers. Parsing itself is transient, with panic recovery returning errors for bad input.

## Dependencies And Integration Points
Used by many SSTable datadriven tests. Integrates `Reader`, `RawWriter`, `blobtest.Values`, `keyspan`, `testkeys`, Bloom policies, and comparer selection.

## Risks And Edge Cases
Ignoring unknown writer-option keys is explicitly noted as error-prone. Blob parsing requires a non-nil blob test value registry. `force-obsolete` is rejected for range deletions. Returned `ReadAll` values clone keys/spans to avoid iterator buffer lifetimes.

## Test Signals
Signals are successful parse/write/read cycles and clear wrapped errors identifying the failed parsed item.
