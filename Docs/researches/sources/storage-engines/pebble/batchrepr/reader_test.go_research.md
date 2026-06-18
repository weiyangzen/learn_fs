# sources/storage-engines/pebble/batchrepr/reader_test.go

## Purpose
This test file validates the batch representation reader and its defensive behavior on malformed binary input. It is important because reader failures surface as corruption during WAL replay or `Batch.SetRepr`.

## Important APIs, Types, And Functions
`TestReader` drives `IsEmpty`, `ReadHeader`, `Read`, and `Reader.Next` through datadriven hex input. `readRepr` converts whitespace/comment-tolerant hex fixtures into bytes. `TestDecodeStr`, `TestDecodeBlobFileIDs`, and `TestReaderNextTruncated` directly target decoder edge cases.

## Control Flow
Datadriven commands either report emptiness or scan a representation, printing header and each decoded record until EOF or error. `readRepr` strips comments and whitespace line-by-line, then hex-decodes. Direct tests enumerate malformed slices and assert `ok=false` without panics. Slow-path `DecodeStr` tests pad input above 128 bytes to force the unsafe unrolled decoder.

## State And Persistence Behavior
The file does not persist data, but it simulates persisted batch/WAL bytes. It confirms that corrupt or truncated record payloads fail cleanly with errors rather than advancing undefined state or panicking.

## Dependencies And Integration Points
Dependencies include `datadriven`, `crstrings`, `require`, `encoding/hex`, `encoding/binary`, and `internal/base`. Fixtures under `batchrepr/testdata/reader` provide regression vectors for representation formatting and error text.

## Risks And Edge Cases
Covered risks include empty input, short headers, truncated one-byte and multi-byte varints, declared lengths exceeding payload, missing values after a valid key, blob count values exceeding remaining data, and huge blob counts that previously could panic during allocation.

## Test Signals
Signals are strong for decoder robustness and output formatting. They do not prove semantic validity of every internal key kind beyond `Reader.Next`'s structural parsing; higher-level batch tests cover kind-specific behavior.
