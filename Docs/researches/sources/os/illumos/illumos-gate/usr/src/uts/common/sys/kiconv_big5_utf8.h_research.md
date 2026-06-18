# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/kiconv_big5_utf8.h

This report was synthesized from ordered chunk research outputs.

## Chunk Map

- chunk 1: lines 1-8444, source bytes 262140, report `Docs/researches/chunks/chunk_sources_os_illumos_illumos_gate_usr_src_uts_common_sys_kiconv_big5_utf8__4d8094fe16ef_research.md`
- chunk 2: lines 8445-13808, source bytes 166096, report `Docs/researches/chunks/chunk_sources_os_illumos_illumos_gate_usr_src_uts_common_sys_kiconv_big5_utf8__ca3270b4f410_research.md`

## Chunk Research

### Chunk 1: lines 1-8444

# Chunk Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/kiconv_big5_utf8.h lines 1-8444

## Scope

This report covers lines 1-8444 of `sources/os/illumos/illumos-gate/usr/src/uts/common/sys/kiconv_big5_utf8.h` for `learn_fs` subset A. The file is a kernel iconv data header for BIG-5 to UTF-8 conversion. This chunk starts at the license and include guard, opens the kernel-only mapping table, and ends inside the table initializer at key `0xd7cb`. It does not include the closing table initializer, `_KERNEL` guard close, C++ extern close, or header guard close.

The reviewed line slice has 8,363 mapping rows. The whole file declares 13,718 rows, matching `KICONV_BIG5_UTF8_MAX`, so later chunk(s) must account for the remaining 5,355 rows.

## Public Surface And APIs

This chunk exposes two kernel-only declarations when `_KERNEL` is defined:

- `#define KICONV_BIG5_UTF8_MAX (13718)` records the total mapping-table item count for BIG-5 to UTF-8 conversion.
- `static kiconv_table_array_t kiconv_big5_utf8[] = { ... }` begins a translation table from BIG-5 code values to UTF-8 byte arrays.

The data type comes from `kiconv_cck_common.h`:

- `kiconv_table_array_t` has `uint32_t key` and `uchar_t u8[4]`.
- Rows in this chunk use a BIG-5 code as `key` and a UTF-8 byte initializer as `u8`.
- Most rows initialize three UTF-8 bytes; 118 rows in this chunk initialize two bytes and rely on C zero-fill for the rest of `u8[4]`.

The header is wrapped for C++ with `extern "C"`, but this chunk declares static data only, not callable functions.

## Data Layout Visible In This Chunk

The file begins with CDDL and Unicode data-file permission notices, then a Sun modification notice. The include guard is `_SYS_KICONV_BIG5_UTF8_H`.

The mapping table starts at line 81. The first row is:

- `0x0000 -> EF BF BD`, replacement character `U+FFFD`, used as a sentinel/fallback mapping row.

The actual BIG-5 table begins at `0xa140` and proceeds in ascending key order through this chunk's final key `0xd7cb`. The visible ranges include standard BIG-5 punctuation, symbols, kana-like and Greek/Cyrillic blocks, Bopomofo, radicals, and a large run of CJK ideograph mappings represented as UTF-8 byte triples.

Within lines 1-8444:

- Mapping rows counted: 8,363.
- First key: `0x0000`.
- Last key: `0xd7cb`.
- Duplicate keys found in this chunk: none.
- Key ordering checked as strictly ascending.
- UTF-8 byte initializer widths: 8,245 rows with three explicit bytes, 118 rows with two explicit bytes.

The chunk boundary is clean at the end of a table row:

- line 8444: `0xd7cb, { 0xE8, 0xA8, 0xAC },`
- line 8445 continues with `0xd7cc`, so the next chunk can continue row-by-row without repairing a split initializer.

## Control Flow

There is no executable control flow in this chunk. Runtime behavior is supplied by the kernel iconv implementation that consumes CCK conversion tables:

1. BIG-5 input validation is defined separately in `kiconv_tc.h` with `KICONV_TC_IS_BIG5_1st_BYTE()` and `KICONV_TC_IS_BIG5_2nd_BYTE()`.
2. A BIG-5 byte pair is combined into a table key.
3. Generic CCK conversion code can binary-search a sorted `kiconv_table_array_t` table using `kiconv_binsearch()`.
4. On match, the `u8` byte array is copied to the UTF-8 output stream.
5. On failure, caller policy decides whether to report an invalid sequence or use replacement behavior.

The conversion-name registry in `uts/common/os/kiconv.c` maps `big5`, `cp950`, and `950` to the same code ID, making this table part of the traditional Chinese BIG-5/CP950 kernel conversion surface.

## State And Dependencies

All state in this chunk is immutable static table data compiled into each translation unit that includes this header under `_KERNEL`.

Direct dependencies visible or required by this chunk:

- `_KERNEL`: hides the table from non-kernel builds.
- `kiconv_table_array_t`: supplied by `uts/common/sys/kiconv_cck_common.h`.
- `uchar_t` and `uint32_t`: supplied through illumos kernel/system type headers included before this generated data header.
- `uts/common/sys/Makefile`: exports `kiconv_big5_utf8.h` alongside related kiconv table headers.
- `kiconv_utf8_big5.h`: companion reverse-direction table, with `KICONV_UTF8_BIG5_MAX (13711)`.
- `kiconv_hkscs_utf8.h` and `kiconv_cp950hkscs_utf8.h`: adjacent Traditional Chinese variants for HKSCS/CP950-HKSCS.
- `kiconv_tc.h`: Traditional Chinese byte-validation macros for BIG-5 and EUC-TW.

## Risks And Invariants

The main invariants are table count, sorted keys, valid UTF-8 byte sequences, and agreement between `KICONV_BIG5_UTF8_MAX` and the full initializer length.

Risks visible in this chunk:

- Generated-data drift: hand edits can silently break individual mappings while preserving C syntax.
- Count mismatch: `KICONV_BIG5_UTF8_MAX` is 13,718, but this chunk only contains the first 8,363 rows; validation must include later chunk(s).
- Include-time duplication: the table is `static` in a public-style header, so every including translation unit gets a private copy. That is likely intentional for the kiconv module pattern but raises footprint risk if included broadly.
- Zero-fill dependence: rows with two-byte UTF-8 initializers depend on `u8[4]` zero-initialization for termination/padding. Consumers must not assume every row has three explicit bytes.
- Encoding validity depends on external BIG-5 byte checks. This table maps keys; it does not itself reject malformed byte sequences.
- Symbol discoverability is weak in this checkout: direct textual references to `kiconv_big5_utf8` outside this header were not found under `usr/src`, so consumers may include or generate references indirectly.

## Cross-Chunk References

Later chunk(s) must continue from `0xd7cc` at line 8445 through the closing row `0xf9dc` and table terminator at line 13800. They should verify:

- Remaining row count is 5,355.
- Whole-file row count remains exactly 13,718.
- No duplicate or nonascending BIG-5 keys appear after `0xd7cb`.
- Closing preprocessor structure remains `#endif /* _KERNEL */`, C++ close, and `#endif /* _SYS_KICONV_BIG5_UTF8_H */`.

### Chunk 2: lines 8445-13808

# Chunk Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/kiconv_big5_utf8.h lines 8445-13808

## Scope

This report covers lines 8445-13808 of `sources/os/illumos/illumos-gate/usr/src/uts/common/sys/kiconv_big5_utf8.h` for `learn_fs` subset A. The chunk is the final ordered segment of the kernel Big5-to-UTF-8 mapping table. It begins at the table entry for Big5 code `0xd7cc` and reaches EOF, including the closing initializer and header guards.

## Public Surface And APIs

This chunk does not introduce new APIs, macros, functions, typedefs, or exported declarations. It contributes data to the file-level static kernel table declared earlier as:

- `static kiconv_table_array_t kiconv_big5_utf8[]`
- `KICONV_BIG5_UTF8_MAX`, defined before this chunk as `13718`

Each visible table element has a 16-bit Big5 key and a three-byte UTF-8 payload stored in the `u8[4]` member of `kiconv_table_array_t`. The shared type comes from `kiconv_cck_common.h`:

- `uint32_t key`
- `uchar_t u8[4]`

The fourth `u8` slot is left zero-initialized by the three-byte brace initializers in this table.

## Data Layout Visible In This Chunk

The chunk contains 5,355 mapping entries. The first entry is:

- line 8445: `0xd7cc -> { 0xE8, 0xA8, 0x9E }`

The final entry is:

- line 13799: `0xf9dc -> { 0xE5, 0xAB, 0xBA }`

Entries are monotonically ascending by Big5 key across this chunk. The ordering follows Big5 byte-space conventions: trail bytes run through `0x7e`, then resume at `0xa1`, so transitions such as `0xd7fe -> 0xd840`, `0xdffe -> 0xe040`, and later lead-byte boundaries are intentional table-order transitions rather than gaps in source ordering.

Most payloads are ordinary three-byte UTF-8 encodings for CJK code points and compatibility ideographs. The range includes a few private/compatibility-looking UTF-8 sequences, for example `0xddfc -> { 0xEF, 0xA8, 0x8D }`, so consumers should treat the byte payloads as authoritative table data rather than recomputing from Unicode scalar order.

## Control Flow

There is no executable control flow in this chunk. Runtime behavior is data-driven in the conversion code that includes this header:

1. A Big5 input code is assembled by a caller outside this file.
2. Conversion logic searches or indexes the sorted `kiconv_big5_utf8[]` table using the Big5 key.
3. The matching `u8` bytes are copied to the UTF-8 output buffer.
4. Unknown keys are handled by caller-side conversion/error logic, not by this table.

The correctness property visible here is therefore table ordering and entry integrity, not branch behavior.

## State And Dependencies

All state in this chunk is static initializer data compiled only under `_KERNEL`. The chunk closes:

- the `kiconv_big5_utf8[]` initializer at line 13800
- the `_KERNEL` conditional at line 13802
- the C++ `extern "C"` block at lines 13804-13806
- the `_SYS_KICONV_BIG5_UTF8_H` include guard at line 13808

Dependencies visible from adjacent context are:

- `kiconv_table_array_t` from `usr/src/uts/common/sys/kiconv_cck_common.h`
- integer and byte types such as `uint32_t` and `uchar_t`
- external conversion code that includes this generated/static mapping header

No mutable globals, locks, allocation, I/O, or filesystem-specific state appear in this chunk.

## Risks And Invariants

Key risks are data-table risks:

- The whole table must remain sorted by `key`; binary-search consumers would fail or return wrong mappings if entries are reordered.
- `KICONV_BIG5_UTF8_MAX` must match the full table size declared before this chunk. This chunk alone contains 5,355 entries and relies on chunk 1 for the earlier 8,363 entries plus the `0x0000` replacement entry.
- Big5 trail-byte gaps are meaningful. Automated normalization that tries to fill or compress missing `0x7f-0xa0` byte positions would corrupt the mapping.
- Each three-byte payload relies on zero-initialization of the fourth `u8[4]` byte. Code must not assume a four-byte UTF-8 sequence is present unless the table explicitly initializes four bytes elsewhere.
- Because this is static generated mapping data, manual edits are high risk and difficult to review semantically; validation should prefer generated-source comparison or round-trip conversion tests.

## Cross-Chunk References

Chunk 1 must contain the file header, include guards, `_KERNEL` wrapper, `KICONV_BIG5_UTF8_MAX`, the start of `kiconv_big5_utf8[]`, and entries through the predecessor of `0xd7cc`. This chunk provides the final entries and closes the table and preprocessor structure, so the merged per-file report should describe the file as one complete static Big5-to-UTF-8 kernel conversion table rather than separate functional modules.
