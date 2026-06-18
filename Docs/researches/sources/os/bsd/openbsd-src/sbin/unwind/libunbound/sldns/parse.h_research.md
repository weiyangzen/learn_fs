# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/sldns/parse.h

`parse.h` declares the low-level parsing/tokenization API. It defines delimiter sets for normal DNS whitespace parsing, newline-preserving parsing, and space skipping, plus maximum line and keyword lengths.

The header defines zone-file directive IDs for `$TTL`, `$ORIGIN`, and `$INCLUDE`, with the directive lookup table implemented in `parse.c`.

The public API covers file token reads, line-number-aware token reads, buffer token reads with optional cross-call parenthesis state, keyword/data extraction, single-character buffer reads, and skip-character helpers. The buffer-token API documents the key contract: callers that pass a parenthesis state must verify it returns to zero after the complete record is parsed.
