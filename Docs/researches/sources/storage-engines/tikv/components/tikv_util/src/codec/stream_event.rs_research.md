# sources/storage-engines/tikv/components/tikv_util/src/codec/stream_event.rs

Purpose: encodes and iterates streams of key/value events where each event is `[key_len_le][key][value_len_le][value]`, with optional key prefix rewriting during iteration.

Important APIs: `Rewrite<'a>` stores `from` and `to` prefixes; trait `Iterator` defines `next`, `valid`, `key`, and `value`; `EventIterator` parses event buffers and can be created with `new()` or `with_rewriting()`; `EventEncoder::encode_event()` returns four slice-like parts; `decode_event()` is a test helper.

Control flow: `EventIterator::next()` checks validity, reads a little-endian key length, copies or rewrites the key into `key_buf`, reads value length, records value offset/length, and advances the buffer offset. `get_next()` returns `None` when invalid or advances and returns the current key/value. Prefix rewriting replaces `from` only when the encoded key starts with that prefix.

State and persistence: iterator state is offset, current value offset/length, reusable key buffer, and optional rewrite rule. Encoded events are byte buffers supplied by the caller; no persistence occurs in this module.

Dependencies and integration: uses `byteorder`, `bytes::{Buf, Bytes}`, standard I/O cursor utilities, and crate `Either` to return stack-owned length arrays or borrowed key/value slices without concatenating.

Risks: parsing assumes the buffer is well-formed; `get_size()` and slice ranges can panic on truncated data rather than returning codec errors. Key data is copied into `key_buf`, while values borrow the source buffer. `EventEncoder` truncates lengths above `u32::MAX` by cast if misused with enormous slices.

Test signals: local tests generate random key/value events, verify encode/decode, iterate multiple events, and validate prefix rewriting behavior.
