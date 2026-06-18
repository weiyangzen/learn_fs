# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/sldns/parse.c

`parse.c` implements low-level tokenizers for DNS-style presentation text from either `FILE*` streams or `sldns_buffer` objects. It understands zone-file features: semicolon comments, quoted strings, escaped characters, parenthesized multiline records, configurable delimiters, CR normalization, and optional line-number tracking.

The file-based path is centered on `sldns_fget_token_l()`, with wrappers for default line tracking. It skips comments, collapses continuation newlines inside parentheses to spaces, avoids returning blank-only lines as tokens, enforces caller-provided limits, and returns errors for unbalanced parentheses or overlong tokens.

The buffer-based path mirrors that behavior with `sldns_bget_token_par()`. It can preserve parenthesis state across calls through a caller-provided `par` pointer, which is used by higher-level RR parsing for multi-token RDATA handling.

Keyword helpers read `keyword<delimiter>data` pairs from files or buffers. Skip helpers advance over sets of characters for both backends, and `sldns_bgetc()` provides a `getc()` equivalent over `sldns_buffer`.

This file is foundational for zone-file and resolver-config parsing; it deliberately returns tokens rather than interpreting DNS RDATA semantics.
