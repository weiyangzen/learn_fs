# File Research: sources/windows/reactos/drivers/filesystems/ext2/src/nls/nls_cp852.c

Purpose: Generated Linux-style NLS module for DOS/OEM code page 852, used for Central European filename character conversion in the ReactOS Ext2 driver copy.

Core structures and data:
- `charset2uni[256]` maps every CP852 byte to Unicode, with ASCII/control identity mappings, Central European Latin letters, box drawing, block elements, and spacing diacritics.
- Reverse lookup pages `page00`, `page01`, `page02`, and `page25` map Unicode pages 0x00, 0x01, 0x02, and 0x25 back to single CP852 bytes.
- `page_uni2charset[256]` dispatches Unicode high bytes to those reverse pages, leaving other pages unmapped.
- `charset2lower[256]` and `charset2upper[256]` implement byte-level case folding for ASCII plus CP852-specific Latin letters.

Important behavior:
- `uni2char()` splits a Unicode `wchar_t` into high/low bytes, selects a reverse page, emits one byte when the page entry is nonzero, returns `-ENAMETOOLONG` for no output room, and returns `-EINVAL` for unmapped Unicode.
- `char2uni()` directly indexes `charset2uni[*rawstring]`, rejects `0x0000`, and returns one consumed byte.
- The registered `struct nls_table` charset name is `"cp852"` with no alias.

Dependencies and interfaces:
- Uses Linux kernel/NLS headers and APIs: `struct nls_table`, `register_nls()`, `unregister_nls()`, `module_init`, `module_exit`, and `THIS_MODULE`.
- No external NLS backend, allocation, locks, filesystem I/O, or mutable runtime state beyond NLS registration.

Design notes and risks:
- The zero sentinel means Unicode NUL and byte 0x00 are not converted successfully by the callbacks.
- `char2uni()` does not check `boundlen`; correctness depends on the NLS caller passing at least one byte.
- The generated arrays are positional and not declared `const`, so accidental edits or writes can silently corrupt filename conversion and case folding.
