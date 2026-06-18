# File Research: sources/windows/reactos/drivers/filesystems/ext2/src/nls/nls_cp936.c

This report was synthesized from ordered chunk research outputs.

## Chunk Map

- chunk 1: lines 1-3840, source bytes 262094, report `Docs/researches/chunks/chunk_sources_windows_reactos_drivers_filesystems_ext2_src_nls_nls_cp936_c_1_1_d2ea7012f8ed_research.md`
- chunk 2: lines 3841-7884, source bytes 262088, report `Docs/researches/chunks/chunk_sources_windows_reactos_drivers_filesystems_ext2_src_nls_nls_cp936_c_2_3_467c486ce831_research.md`
- chunk 3: lines 7885-11031, source bytes 198722, report `Docs/researches/chunks/chunk_sources_windows_reactos_drivers_filesystems_ext2_src_nls_nls_cp936_c_3_7_ba0c86810d37_research.md`

## Chunk Research

### Chunk 1: lines 1-3840

# Chunk Research: sources/windows/reactos/drivers/filesystems/ext2/src/nls/nls_cp936.c lines 1-3840

## Scope

This chunk covers the opening 3,840 lines of the generated ReactOS Ext2 NLS source for code page 936. The file belongs to `sources/windows/reactos`, which is included by `Docs/research_subset_a.md`.

The visible range contains the file provenance comment, Linux NLS headers, and the first large block of CP936 byte-to-Unicode lookup tables. It starts `static wchar_t c2u_81[256]` and continues through the beginning of `static wchar_t c2u_ED[256]`; the range ends in the middle of `c2u_ED`.

## APIs and Entry Points

- No callable function or exported API is defined in this chunk.
- The chunk declares static data arrays named `c2u_81` through `c2u_ED`, one array per possible high byte/lead byte of the CP936 double-byte encoding.
- The arrays are intended for later use through `page_charset2uni[256]`, which is declared after the complete `c2u_*` table block outside this chunk.
- Later file code, outside this range, wires the tables into Linux-style NLS callbacks `char2uni` and `uni2char`, then registers a `struct nls_table` for charset `cp936` with alias `gb2312`.

## Control Flow

There is no local control flow in this chunk. Runtime behavior is table-driven:

- A later decoder reads the first byte of an input string as `ch`.
- If `page_charset2uni[ch]` points to one of these `c2u_*` arrays, the second byte `cl` indexes directly into the 256-entry `wchar_t` page.
- A nonzero table value is a Unicode code point; `0x0000` represents an unmapped or invalid byte pair.

Because the range is only data, all branch behavior, input length checks, ASCII fallback, and NLS registration happen in later chunks.

## State and Data Flow

- The chunk stores immutable mapping state as `static wchar_t` arrays, though the declarations are not `const`.
- Each complete table maps `CP936 high byte + low byte` to one Unicode `wchar_t` value.
- Most arrays reserve low-byte ranges `0x00-0x3F` as `0x0000`, with populated mappings beginning at low byte `0x40`.
- Many rows deliberately end with `0x0000` at low byte `0x7F` and `0xFF`, matching invalid CP936 byte positions.
- Visible Unicode outputs include CJK unified ideographs, compatibility/private compatibility values such as `0xF91B`, `0xF92D`, `0xF978`, `0xFA15`, and mixed GBK/CP936 extension mappings.
- `c2u_A4` through `c2u_AF` are shorter initializer blocks than the regular 35-line pages, relying on zero-fill for omitted trailing entries.
- The chunk ends after the first 80 initialized entries of `c2u_ED`; the remainder of `c2u_ED` is in the next chunk.

Complete arrays in this chunk:

- `c2u_81` through `c2u_A3`
- `c2u_A4` through `c2u_AF`, with sparse/truncated initializers
- `c2u_B0` through `c2u_EC`

Partial array in this chunk:

- `c2u_ED`, starting at line 3830 and continuing beyond line 3840

## Dependencies

- Includes Linux kernel/NLS headers: `<linux/module.h>`, `<linux/kernel.h>`, `<linux/string.h>`, `<linux/nls.h>`, and `<linux/errno.h>`.
- Depends on `wchar_t` and Linux NLS infrastructure supplied by those headers.
- Depends on later local declarations of `page_charset2uni`, reverse `u2c_*` tables, case-folding tables, `char2uni`, `uni2char`, and `struct nls_table`.
- The opening comment says the table was automatically generated from Microsoft CP936/Unicode data; maintainers should treat it as generated mapping data rather than hand-authored logic.

## Risks and Edge Cases

- The data is declared `static` but not `const`, so it may occupy writable storage even though it is lookup-only.
- A split or merge error around this chunk boundary would leave `c2u_ED` incomplete and break compilation or corrupt the mapping table.
- Consumers must distinguish `0x0000` as an invalid mapping sentinel from valid Unicode output; the later decoder rejects `0x0000` after table lookup.
- Sparse/truncated arrays rely on C zero-initialization. Mechanical regeneration or conversion to another format must preserve that behavior.
- Mapping correctness is security-relevant for filesystem names: wrong byte-to-Unicode conversion can cause name aliasing, failed lookup, or inconsistent case handling when filenames contain CP936 multibyte sequences.
- These tables do not perform bounds checks themselves. Safety depends on later code only indexing arrays with `unsigned char` values and checking input length before reading a second byte.

## Cross-Chunk References

- Next chunk must continue and close `c2u_ED`, then continue the remaining `c2u_EE` through `c2u_FE` pages.
- Later chunks define `page_charset2uni[256]`, which maps lead bytes `0x81-0xFE` to the `c2u_*` arrays declared here and leaves other lead bytes `NULL`.
- Later chunks define reverse Unicode-to-CP936 `u2c_*` tables and `page_uni2charset[256]`; those are the counterpart path for `uni2char`.
- Later chunks define `charset2lower` and `charset2upper`, which provide byte-level case conversion for the registered NLS table.
- The final executable behavior appears near the end of the file in `uni2char`, `char2uni`, `init_nls_cp936`, `exit_nls_cp936`, `module_init`, and `module_exit`; this chunk only supplies part of their lookup state.

### Chunk 2: lines 3841-7884

# Chunk Research: sources/windows/reactos/drivers/filesystems/ext2/src/nls/nls_cp936.c lines 3841-7884

## Scope

This chunk is the middle of the generated CP936/GB2312 NLS conversion table used by the ReactOS ext2 filesystem driver copy of `linux/fs/nls_cp936.c`. It is in subset A because `sources/windows/reactos` is included by `Docs/research_subset_a.md`.

The chunk contains generated static lookup data only. It does not define executable functions, module registration, or exported symbols. Adjacent context shows the source file is a Linux NLS table implementation with `uni2char()`, `char2uni()`, `struct nls_table table`, `register_nls()`, and `unregister_nls()` later in the file.

## APIs And Exports

- No public APIs or exports are declared in this chunk.
- Visible static data contributes to the private implementation of the file-local NLS callbacks:
  - `char2uni()` uses `page_charset2uni[ch]` to decode a CP936 lead byte plus trail byte into a `wchar_t`.
  - `uni2char()` uses `page_uni2charset[ch]` to encode a Unicode `wchar_t` into one or two CP936 bytes.
- The chunk defines or partially defines lookup arrays, all with internal linkage:
  - Tail of `static wchar_t c2u_ED[256]`, which starts before the chunk.
  - Full `static wchar_t c2u_EE[256]` through `static wchar_t c2u_FE[256]`.
  - `static wchar_t *page_charset2uni[256]`, the first-level dispatch table for CP936 lead bytes.
  - Full `static unsigned char u2c_01[512]`, `u2c_02[512]`, `u2c_03[512]`, `u2c_04[512]`, `u2c_20[512]` through `u2c_26[512]`, `u2c_30[512]` through `u2c_33[512]`, and `u2c_4E[512]` through `u2c_75[512]`.
  - Beginning of `static unsigned char u2c_76[512]`, which continues past the chunk.

## Data Layout

The `c2u_*` arrays are two-byte CP936-to-Unicode pages. The high byte selects a page through `page_charset2uni[]`; the low byte indexes the selected 256-entry `wchar_t` array. Entries with `0x0000` are unmapped/invalid for two-byte decoding. In this chunk, most `c2u_EE` through `c2u_FE` pages reserve low byte ranges `0x00-0x3F`, include valid mappings for `0x40-0x7E`, skip `0x7F`, and continue valid mappings for much of `0x80-0xFE`, matching CP936 trail-byte shape.

`page_charset2uni[256]` is the central dispatch array for decoding. It maps lead bytes `0x81-0xFE` to `c2u_81` through `c2u_FE` and leaves unsupported lead bytes as `NULL`. The file intentionally leaves `0xFF` as `NULL`.

The `u2c_*` arrays are Unicode-to-CP936 pages. The Unicode high byte selects a page through `page_uni2charset[]` later in the file; the Unicode low byte indexes a 512-byte page as `low * 2`. Each entry pair is the CP936 byte sequence for that Unicode code point. A pair of `0x00, 0x00` marks an unmapped Unicode value. This chunk covers low Unicode pages and a large contiguous block from Unicode high byte `0x4E` through part of `0x76`, including many CJK Unified Ideograph ranges.

## Control Flow

There is no control flow inside the chunk. Runtime behavior is table-driven:

1. Decode path: `char2uni()` reads the first input byte as `ch`. If only one byte is available, it returns that byte as a single-byte character. Otherwise it looks up `page_charset2uni[ch]`; when the page pointer exists and the second byte is nonzero, it returns `page[cl]` unless that entry is `0x0000`. If no page exists, it falls back to a one-byte character.
2. Encode path: `uni2char()` splits `wchar_t uni` into high byte `ch` and low byte `cl`, looks up `page_uni2charset[ch]`, and reads two bytes at `cl * 2`. A `0x00, 0x00` pair is invalid. If no page exists and `ch == 0 && cl != 0`, it emits the low byte as a single-byte character.

The chunk’s `page_charset2uni[]` is directly used by the decode path; the chunk’s `u2c_*` tables are used indirectly after `page_uni2charset[]` is defined in a later chunk.

## State And Dependencies

All data in this chunk is immutable static storage. There is no allocation, locking, reference counting, mutation, or per-open filesystem state.

The data depends on Linux NLS types and callback contracts from the includes at the top of the file: `<linux/module.h>`, `<linux/kernel.h>`, `<linux/string.h>`, `<linux/nls.h>`, and `<linux/errno.h>`. The surrounding file binds these tables into a `struct nls_table` named `cp936` with alias `gb2312`.

## Risks

- The generated arrays are positional. Any insertion, deletion, or misordered initializer silently changes character mappings.
- `page_charset2uni[]` and the `c2u_*` declarations must remain synchronized; a wrong pointer maps an entire CP936 lead-byte page to unrelated Unicode code points.
- `u2c_*` pages must remain synchronized with the later `page_uni2charset[]` dispatch table; wrong high-byte dispatch corrupts Unicode-to-CP936 encoding.
- Invalid mappings are represented by sentinel zeros. Accidental nonzero data can make invalid byte sequences appear valid; accidental zeros can reject valid filenames.
- The chunk starts inside `c2u_ED` and ends inside `u2c_76`, so complete validation of those two arrays requires adjacent chunks.
- File names on ext2 volumes mounted through this NLS table can be mis-decoded or become unroundtrippable if either direction is edited inconsistently.

## Cross-Chunk References

- Earlier chunk content defines the beginning of the file, all `c2u_81` through most of `c2u_ED`, and the comments identifying this as an automatically generated Microsoft CP936 table.
- This chunk defines `page_charset2uni[]`, which references many `c2u_*` arrays from both earlier lines and this chunk.
- Later chunk content completes `u2c_76`, defines `u2c_77` and later Unicode-to-charset pages, defines `page_uni2charset[]`, adds ASCII case-conversion tables, and defines the `uni2char()`, `char2uni()`, NLS table, and module init/exit routines that consume the data.

### Chunk 3: lines 7885-11031

# Chunk Research: sources/windows/reactos/drivers/filesystems/ext2/src/nls/nls_cp936.c lines 7885-11031

## Scope

This chunk covers the tail of ReactOS ext2's imported Linux `nls_cp936.c` CP936/GB2312 NLS module. Most of the chunk is generated Unicode-to-charset table data; the final section wires those tables into the Linux-style `struct nls_table` conversion API and module registration path.

## APIs and Entry Points

- `uni2char(const wchar_t uni, unsigned char *out, int boundlen)` converts one Unicode code point to CP936 bytes using `page_uni2charset`; it returns byte count `1` or `2`, or `-ENAMETOOLONG` / `-EINVAL` on failure (`10945-10974`).
- `char2uni(const unsigned char *rawstring, int boundlen, wchar_t *uni)` converts one CP936 input character to a Unicode code point using `page_charset2uni`; it returns consumed byte count `1` or `2`, or a negative error (`10976-11005`).
- `table` exposes charset name `"cp936"`, alias `"gb2312"`, conversion callbacks, case tables, and `THIS_MODULE` owner through the kernel NLS interface (`11007-11015`).
- `init_nls_cp936()` registers the NLS table with `register_nls(&table)` (`11017-11020`).
- `exit_nls_cp936()` unregisters it with `unregister_nls(&table)` (`11022-11025`).
- `module_init`, `module_exit`, `MODULE_LICENSE`, and `MODULE_ALIAS_NLS(gb2312)` declare kernel module lifecycle and metadata (`11027-11031`).

## Data and State

- The chunk starts in the final rows of `u2c_76` from the previous chunk and then defines Unicode page tables `u2c_77` through `u2c_9F`, plus sparse/special tables `u2c_DC`, `u2c_F9`, `u2c_FA`, `u2c_FE`, and `u2c_FF` (`7885-10836`). Each `u2c_*` table stores 512 bytes, two output bytes per Unicode low byte, with `0x00,0x00` marking unmapped characters.
- `page_uni2charset[256]` maps a Unicode high byte to the corresponding `u2c_*` table pointer or `NULL` when that Unicode page is unsupported (`10838-10871`). This array is the main dispatch table for `uni2char`.
- `charset2lower[256]` and `charset2upper[256]` are bytewise case-fold tables. They only fold ASCII letters (`A-Z` / `a-z`); all bytes `0x80-0xff` map to themselves (`10873-10943`).
- Module state is effectively static and read-only after load. There is no mutable runtime state in this chunk beyond NLS core registration/unregistration of the static `table`.

## Control Flow

- Unicode-to-CP936:
  - Rejects empty output capacity with `-ENAMETOOLONG` (`10953-10954`).
  - Splits `wchar_t uni` into high byte `ch` and low byte `cl` (`10949-10950`).
  - Looks up `page_uni2charset[ch]` (`10957`).
  - If a table exists, requires two output bytes, copies `uni2charset[cl*2]` and `[cl*2+1]`, rejects the zero pair as unmapped, and returns `2` (`10958-10965`).
  - If there is no table and the Unicode character is non-NUL ASCII (`ch == 0 && cl`), writes one byte and returns `1` (`10966-10968`).
  - Otherwise returns `-EINVAL` (`10970-10971`).
- CP936-to-Unicode:
  - Rejects zero/negative input length with `-ENAMETOOLONG` (`10983-10984`).
  - If only one byte is available, treats it as a single-byte character and returns it directly as Unicode (`10986-10988`).
  - With at least two bytes, uses first byte `ch` as the page index and second byte `cl` as the table offset (`10991-10996`).
  - If `page_charset2uni[ch]` exists and `cl` is nonzero, reads the mapped Unicode value, rejects `0x0000`, and returns `2` (`10994-10999`).
  - Otherwise it falls back to treating `ch` as a single-byte Unicode value and returns `1` (`11000-11003`).

## Dependencies

- Includes and kernel/NLS types are outside this chunk: `<linux/module.h>`, `<linux/kernel.h>`, `<linux/string.h>`, `<linux/nls.h>`, and `<linux/errno.h>` appear at file top (`10-14`).
- `page_charset2uni`, used by `char2uni`, is defined before this chunk from the `c2u_81` through `c2u_FE` tables (`4400-4433`); this chunk depends on that earlier generated decoder table block.
- `register_nls`, `unregister_nls`, `struct nls_table`, `THIS_MODULE`, `module_init`, `module_exit`, `MODULE_LICENSE`, and `MODULE_ALIAS_NLS` are kernel/module/NLS framework APIs.
- Error codes `ENAMETOOLONG` and `EINVAL` come from kernel errno definitions and are returned as negative values.

## Risks and Edge Cases

- `char2uni` returns a lone byte as Unicode whenever `boundlen == 1`, even if that byte is a CP936 lead byte. This is consistent with common Linux NLS table behavior but means truncated DBCS input is not rejected as malformed in this code path (`10986-10988`).
- `char2uni` also falls back to a one-byte character when the first byte has no `page_charset2uni` table or the second byte is zero (`10994-11003`). Invalid lead-byte sequences may therefore be consumed as one byte rather than producing `-EINVAL`.
- `uni2char` rejects Unicode NUL because the ASCII fallback requires `cl` to be nonzero and no table entry represents U+0000 (`10966-10971`).
- The generated tables are dense and manual review is impractical; correctness depends on generation from the Microsoft CP936 mapping source described in the file header (`1-7`). Sparse tables such as `u2c_DC`, `u2c_FE`, and `u2c_FF` intentionally contain many `0x00,0x00` unmapped slots (`10659-10661`, `10746-10836`).
- The lookup math `cl * 2` assumes every `u2c_*` table has 512 bytes. The declarations in this chunk follow that convention, including sparse tables that are declared `[512]` and implicitly zero-filled beyond listed initializers.

## Cross-Chunk References

- Previous chunks define the file header/import provenance, all charset-to-Unicode `c2u_*` decode tables, `page_charset2uni`, and the earlier Unicode-to-charset tables `u2c_01` through most of `u2c_76`.
- This chunk completes the Unicode-to-charset table family and defines `page_uni2charset`, so `uni2char` here depends on data spanning earlier chunks and this chunk.
- The final per-file report should merge this chunk with earlier chunks by treating the file as a generated bidirectional CP936 mapping module with only a small amount of handwritten control code at the end.
