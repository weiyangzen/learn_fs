# File Research: sources/os/linux/linux/fs/nls/nls_cp932.c

This report was synthesized from ordered chunk research outputs.

## Chunk Map

- chunk 1: lines 1-4152, source bytes 262094, report `Docs/researches/chunks/chunk_sources_os_linux_linux_fs_nls_nls_cp932_c_1_1_4152_cd7b667b3ab8_research.md`
- chunk 2: lines 4153-7934, source bytes 229129, report `Docs/researches/chunks/chunk_sources_os_linux_linux_fs_nls_nls_cp932_c_2_4153_7934_2bddfa0fc365_research.md`

## Chunk Research

### Chunk 1: lines 1-4152

# Chunk Research: sources/os/linux/linux/fs/nls/nls_cp932.c lines 1-4152

## Scope

- Repository subset: `Docs/research_subset_a.md`; `sources/os/linux/linux` is explicitly in scope.
- Source span read: lines 1-4152 of `fs/nls/nls_cp932.c`.
- This is chunk 1 of 2 for the Linux NLS CP932/Shift-JIS module. It covers the file prologue, kernel includes, all byte-to-Unicode page tables, the byte-to-Unicode page index, the high-ASCII Unicode table, and the first half of Unicode-to-CP932 page tables.
- The chunk ends inside `u2c_6B[512]`; it does not include the remaining Unicode-to-CP932 tables, case tables, conversion callbacks, `struct nls_table`, registration functions, or module metadata.

## APIs and Data Structures

- Header dependencies in this chunk are `linux/module.h`, `linux/kernel.h`, `linux/string.h`, `linux/nls.h`, and `linux/errno.h`.
- `c2u_81` through `c2u_FC`: 45 `static const wchar_t [256]` byte-to-Unicode pages for CP932 lead bytes `0x81..0x9F`, `0xE0..0xEA`, `0xED..0xEE`, and `0xFA..0xFC`. Entries use `0x0000` as the unmapped sentinel.
- `page_charset2uni[256]`: top-level lead-byte index. It maps valid two-byte CP932 lead bytes to `c2u_*` pages and leaves unsupported lead bytes as `NULL`.
- `u2c_00hi[256 - 0xA0][2]`: special Unicode `U+00A0..U+00FF` reverse table for selected punctuation and signs.
- `u2c_03`, `u2c_04`, `u2c_20` through `u2c_26`, `u2c_30`, `u2c_32`, `u2c_33`, and `u2c_4E` through the first part of `u2c_6B`: reverse lookup pages where each Unicode low byte selects a two-byte CP932 pair.
- Visible mapped ranges include Greek, Cyrillic, punctuation, arrows/math symbols, box drawing, CJK symbols, fullwidth forms, Kana-related values, CJK ideographs from `U+4E00`, and CP932/IBM extension byte pairs.

## Control Flow

There are no functions or executable branches in this chunk. Later callbacks consume these tables:

- CP932-to-Unicode conversion uses ASCII/halfwidth fast paths or indexes `page_charset2uni`; `NULL` pages and `0x0000` entries are invalid.
- Unicode-to-CP932 conversion uses Unicode high-byte table selection in chunk 2, then low-byte `* 2` indexing into these `u2c_*` pages.
- ASCII and halfwidth Katakana fast paths are implemented later, but this chunk’s tables are shaped around those rules.

## State and Dependencies

All data here is `static const`; there is no mutable state, locking, allocation, or reference counting. The generated table comment identifies Microsoft Unicode code page data as the source. Types and contracts come from Linux kernel NLS headers, and these internal-linkage arrays become externally reachable only through the `nls_table` callbacks in chunk 2.

## Risks and Edge Cases

- Table data corruption silently changes filename character conversion for filesystems using NLS `cp932`/`sjis`.
- `0x0000` and `{0x00, 0x00}` are sentinels, not valid generated double-byte mappings.
- `page_charset2uni` must stay synchronized with the defined `c2u_*` pages.
- Reverse pages assume exactly two bytes per Unicode low-byte slot.
- The chunk boundary splits `u2c_6B[512]`; lines 4115-4183 must be treated as one table.
- CP932 vendor/compatibility mappings intentionally differ from strict Shift-JIS/JIS behavior.

## Cross-Chunk References

- Chunk 2 continues `u2c_6B[512]`, then defines remaining `u2c_*` tables, `page_uni2charset`, case tables, conversion callbacks, registration, and module metadata.
- `uni2char` consumes `u2c_00hi` and `u2c_*` pages, returning `-EINVAL` for `{0x00, 0x00}`.
- `char2uni` consumes `page_charset2uni` and `c2u_*`, returning `-EINVAL` for `0x0000`.
- `struct nls_table table` exposes these tables as `.charset = "cp932"` and `.alias = "sjis"`.
- Linux-stable and ReactOS CP932 files are useful comparison points for generated-table drift; no final per-file report was created.

### Chunk 2: lines 4153-7934

# Chunk Research: sources/os/linux/linux/fs/nls/nls_cp932.c lines 4153-7934

## Scope

This chunk is the second and final chunk of `nls_cp932.c`. It starts in the tail of the generated `u2c_6B` Unicode-to-charset page and then contains the remaining Unicode-to-CP932 lookup pages, the Unicode page dispatch table, ASCII-only case-folding tables, both NLS conversion callbacks, and the module registration metadata for the `cp932` / `sjis` native-language-support table.

## APIs and Entry Points

- `uni2char()` is the Unicode-to-CP932 encoder. It returns bytes written, `-ENAMETOOLONG` for too-small output buffers, or `-EINVAL` for unmapped Unicode.
- `char2uni()` is the CP932-to-Unicode decoder. It returns bytes consumed, `-ENAMETOOLONG` for insufficient input, or `-EINVAL` for invalid/unmapped bytes.
- `table` binds charset `"cp932"`, alias `"sjis"`, conversion callbacks, and case tables into Linux NLS.
- `init_nls_cp932()` registers the table; `exit_nls_cp932()` unregisters it.
- `MODULE_ALIAS_NLS(sjis)` exposes the Shift-JIS alias.

## Data, State, and Control Flow

This chunk is mostly immutable generated lookup data: the tail of `u2c_6B`, `u2c_6C` through `u2c_9F`, sparse pages `u2c_DC`, `u2c_F9`, `u2c_FA`, and `u2c_FF`, plus `page_uni2charset[256]`.

`uni2char()` splits `wchar_t` into high/low bytes, handles `U+FF61..U+FF9F` as one-byte halfwidth katakana, dispatches through `page_uni2charset`, rejects `{0x00, 0x00}` sentinel pairs, and special-cases ASCII plus `u2c_00hi` for `U+00A0..U+00FF`.

`char2uni()` decodes ASCII directly, maps bytes `0xA1..0xDF` to `U+FF61..U+FF9F`, then uses previous-chunk `page_charset2uni` and `c2u_*` tables for two-byte sequences.

Case tables are byte-wise and ASCII-only; all bytes `0x80..0xff` are identity mappings.

## Dependencies

- Includes Linux module/NLS/errno interfaces.
- Depends on chunk 1 for `page_charset2uni`, all `c2u_*` reverse tables, `u2c_00hi`, and earlier `u2c_*` pages.
- Depends on `fs/nls/nls_base.c` registration behavior: `register_nls()` inserts `table` into the global NLS list, and `unregister_nls()` removes it.

## Risks and Edge Cases

- Generated tables are trusted; no runtime consistency check confirms forward and reverse mappings agree.
- `uni2char()` writes two bytes before detecting `{0x00, 0x00}` as unmapped, so buffers may be modified on `-EINVAL`.
- ASCII NUL maps successfully as one byte, while table-derived Unicode `0x0000` means invalid.
- `char2uni()` rejects zero trail bytes before lookup.
- `wchar_t` values are effectively truncated to low 16 bits by `ch`/`cl` extraction.
- No Unicode normalization or Japanese/fullwidth case folding is performed.

## Cross-Chunk References

Chunk 1 owns the reverse CP932-to-Unicode tables and early forward pages. This chunk completes the forward table set and owns the actual conversion callbacks and module lifecycle. Any final per-file correctness review must merge both chunks because the two mapping directions are independently table-driven.
