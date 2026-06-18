# File Research: sources/os/bsd/netbsd-src/lib/libc/citrus/citrus_bcs.c

Implements basic character set string helpers used throughout Citrus parsing.

Key behavior:
- Case-insensitive string compare and bounded compare using `_bcs_toupper`.
- Whitespace and non-whitespace skipping, with both unbounded and length-tracked variants.
- Truncates trailing whitespace in a bounded buffer.
- Destructively lowercases or uppercases C strings using BCS conversions.

These routines intentionally avoid locale-sensitive `ctype(3)` behavior so parser behavior is stable while loading locale data.
