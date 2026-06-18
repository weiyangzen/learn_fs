# File Research: sources/windows/reactos/drivers/filesystems/ext2/src/nls/nls_cp866.c

Purpose: Generated NLS module for DOS/OEM code page 866, the common Russian Cyrillic DOS code page.

Core structures and data:
- `charset2uni[256]` maps `0x80-0xaf` to uppercase and lowercase Cyrillic ranges, keeps DOS line drawing in `0xb0-0xdf`, maps `0xe0-0xef` to remaining lowercase Cyrillic, and maps `0xf0-0xff` to Cyrillic variants and symbols.
- Reverse pages `page00`, `page04`, `page21`, `page22`, and `page25` support Latin/symbol, Cyrillic, numero sign, math, and box/block reverse mappings.
- `charset2lower` and `charset2upper` fold CP866 Cyrillic byte ranges as well as ASCII.

Important behavior:
- `uni2char()` returns a single CP866 byte for exact mappings and `-EINVAL` otherwise.
- `char2uni()` rejects byte 0x00 through the `0x0000` sentinel convention.
- The charset registers as `"cp866"` with no alias.

Dependencies and interfaces:
- Uses only Linux kernel NLS/module APIs.
- No runtime allocation or per-mount state.

Design notes and risks:
- CP866's Cyrillic mappings are comparatively regular, but the surrounding graphics and symbol pages still require exact table preservation.
- Case folding maps whole Cyrillic byte ranges, so table corruption can affect case-insensitive lookup semantics.
- As with the other generated modules, Unicode normalization and replacement fallback are absent.
