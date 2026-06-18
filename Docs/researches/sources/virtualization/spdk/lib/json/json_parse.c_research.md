# File Research: sources/virtualization/spdk/lib/json/json_parse.c

Full-file read: 640 lines.

This file implements SPDK’s low-level JSON tokenizer/parser.

Main responsibilities:
- Validate and optionally decode JSON strings in place.
- Decode two-character escapes and Unicode `\uXXXX`, including UTF-16 surrogate pairs.
- Validate number syntax without converting to numeric types.
- Optionally accept C/C++-style comments when the parse flag allows it.
- Parse JSON into a flat `spdk_json_val` token array with begin/end container tokens.
- Report incomplete, invalid, and max-depth errors.

Important control flow:
- `spdk_json_parse` first can be called with `values == NULL` to count tokens and find complete-message boundaries.
- The parser uses a state machine for value, separator, object name, colon, and end states.
- Container starts record their token index so the begin token’s `len` can later be set to contained token count.
- Nesting is capped at `SPDK_JSON_MAX_NESTING_DEPTH` of 64.
- With `SPDK_JSON_PARSE_FLAG_DECODE_IN_PLACE`, string values point into decoded bytes inside the original buffer.

Integration points:
- Used by JSON-RPC request/response parsing and by utility decoders.
- Depends on internal UTF helpers for validation and encoding.

Risks and review notes:
- In-place decode means callers must keep the original mutable buffer alive while using tokens.
- No resynchronization is possible after a streaming parse error; JSON-RPC closes connections on invalid parse.
- Comments are intentionally flag-gated and not JSON-standard.

Testing focus:
- Unicode surrogate validity and incomplete escapes.
- Number grammar edge cases.
- Container length correctness.
- Full/incomplete streaming parse behavior.
