# sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/collation/collator/mod.rs

## Purpose
Collects concrete collator implementations, re-exports them, and provides shared helpers and cross-collation tests.

## APIs, Flow, And State
The module declares binary, UTF8, GBK, GB18030, latin1, and UCA collator modules. It re-exports their public collator types. Shared helpers include `PADDING_SPACE`, `trim_end_padding`, and `next_utf8_char`, a small UTF-8 decoder that returns `(char, remaining_bytes)` or `None`. Tests iterate over multiple `Collation` enum values through `match_template_collator!`, checking compare results, sort hashes, and sort-key bytes for ASCII, accents, Unicode, Chinese text, invalid bytes, no-padding variants, and GB18030/GBK behavior.

## Dependencies And Integration
Depends on the collation trait layer, charset module, TiKV codec prelude, and concrete collator modules. This is the central module consumed by scalar/vector comparisons and sort-key generation.

## Risks And Test Signals
Risks include helper semantics shared by many collators, especially padding and invalid UTF-8 handling. The test matrix is a strong signal because it verifies comparison and hash agreement for equal values and exact sort-key bytes across collations.
