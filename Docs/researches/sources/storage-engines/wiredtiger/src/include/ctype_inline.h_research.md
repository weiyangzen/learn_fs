# sources/storage-engines/wiredtiger/src/include/ctype_inline.h

## Purpose
`ctype_inline.h` wraps standard C character classification/conversion routines so WiredTiger passes unsigned bytes and gets predictable boolean behavior across platforms.

## Important APIs, Types, and Functions
Inline wrappers include `__wt_isalnum`, `__wt_isalpha`, `__wt_isascii`, `__wt_isdigit`, `__wt_isprint`, `__wt_isspace`, and `__wt_tolower`. `__wt_isprint` additionally rejects bytes >= `0x80` even if a platform locale would call them printable.

## Control Flow
Parser, dump, logging, and validation code call these wrappers instead of raw `ctype.h` functions. Each wrapper casts through `u_char` at the function boundary, preventing undefined behavior from negative `char` values.

## State and Persistence Behavior
There is no state or persistence. The durable effect is indirect: consistent parsing/printing rules for configuration, keys, diagnostics, and dumps across build environments.

## Dependencies and Integration Points
The file depends only on `<ctype.h>` and WiredTiger's `WT_INLINE`/`u_char` definitions. It is used anywhere byte-oriented parsing or printable checks must not depend on signed `char` behavior.

## Risks and Edge Cases
Locale-sensitive C library behavior can still affect `isalnum`/`isalpha`/`isspace` unless callers constrain input expectations. The explicit ASCII cap in `__wt_isprint` is intentional but means UTF-8 bytes are not treated as printable by this helper.

## Test Signals
Parser tests with high-bit bytes, signed-char platforms, and locale variation are useful. Unit tests should assert that bytes over `0x7f` are not printable and that digit/space checks match expected ASCII behavior.
