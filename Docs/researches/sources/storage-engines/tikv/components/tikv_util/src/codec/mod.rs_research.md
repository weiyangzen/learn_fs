# sources/storage-engines/tikv/components/tikv_util/src/codec/mod.rs

Purpose: module root for TiKV utility codecs. It exposes byte, number, and stream-event codecs plus shared slice-reading and error handling utilities.

Important APIs: submodules `bytes`, `number`, and `stream_event`; `BytesSlice<'a> = &'a [u8]`; `read_slice(data, size)`; `next_prefix_of(key)`; `Error` variants for I/O, key length/padding/not-found, and value length/meta; `Result<T>`; and `ErrorCodeExt` mapping to codec error codes.

Control flow: `read_slice()` consumes a prefix from a borrowed byte slice or returns unexpected EOF. `next_prefix_of()` walks a key from the end, trimming trailing `0xff` bytes and incrementing the first non-`0xff`; an empty result represents infinity for prefix ranges.

State and persistence: stateless helpers. Errors can be cloned only for non-I/O variants through `maybe_clone()`.

Dependencies and integration: depends on `error_code` and `thiserror`. All codec submodules share this error/result type, giving consistent error-code reporting to higher layers.

Risks: `next_prefix_of(vec![0xff])` returning an empty upper bound is intentional but easy to misuse if callers do not treat empty as infinity. `read_slice()` mutates the input slice pointer, so callers must account for consumed bytes.

Test signals: doctest examples on `next_prefix_of`; submodule tests exercise the shared error type and EOF paths indirectly.
