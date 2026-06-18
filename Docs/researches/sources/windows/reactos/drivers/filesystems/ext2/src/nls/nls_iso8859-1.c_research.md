# File Research: sources/windows/reactos/drivers/filesystems/ext2/src/nls/nls_iso8859-1.c

Purpose: Generated NLS module for ISO 8859-1 / Latin-1, used as a one-byte Western European charset converter.

Core structures and data:
- `charset2uni[256]` is a direct byte-to-Unicode mapping from `U+0000` through `U+00FF`.
- `page00[256]` maps Unicode page 0 back to the same byte values.
- `page_uni2charset[256]` only points Unicode high byte 0 to `page00`; all other pages are zero-filled and unmapped.
- `charset2lower` and `charset2upper` fold ASCII and Latin-1 case pairs.

Important behavior:
- `uni2char()` emits one byte for nonzero page-0 reverse entries and returns `-EINVAL` for all other Unicode pages.
- `char2uni()` maps one input byte but rejects `0x0000`.
- The module registers charset `"iso8859-1"` with no alias.

Dependencies and interfaces:
- Standard Linux `struct nls_table` module with register/unregister lifecycle.
- No external dependencies or dynamic state.

Design notes and risks:
- Although ISO 8859-1 maps byte 0 to Unicode NUL in the data table, the callback treats zero as invalid because zero is also the unmapped sentinel.
- This file is low-complexity compared with other codepages, but the case tables still affect case-insensitive filename behavior.
- No Unicode normalization or fallback mapping is performed.
