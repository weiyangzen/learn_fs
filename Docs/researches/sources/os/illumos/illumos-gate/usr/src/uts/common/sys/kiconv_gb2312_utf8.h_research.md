# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/kiconv_gb2312_utf8.h

## Purpose

`kiconv_gb2312_utf8.h` is a kernel-only illumos iconv data header for converting GB2312 encoded values to UTF-8 byte sequences. It contains no callable functions; its primary payload is a large static mapping table compiled only when `_KERNEL` is defined.

The file carries CDDL, Sun copyright, and Unicode data-file permission notices, with a Sun modification notice. It is guarded by `_SYS_KICONV_GB2312_UTF8_H` and wrapped in `extern "C"` for C++ consumers.

## Public Surface

Under `_KERNEL`, the file defines:

- `KICONV_GB2312_UTF8_MAX (8179)`: the declared number of mapping entries.
- `static uchar_t kiconv_gb2312_utf8[][3]`: a flat array of UTF-8 byte triples.

The table comment says the index is derived from `GB2312 - 0x2121`, so consumers must preserve the same GB2312 normalization/indexing convention used by the conversion implementation. The header itself does not validate input bytes or compute indexes.

## Data Layout

The table contains exactly 8,179 initializer rows, matching `KICONV_GB2312_UTF8_MAX`.

Observed table characteristics:

- 8,029 rows have three explicit bytes.
- 150 rows have two explicit bytes and rely on zero-initialization of the third byte.
- 729 rows map to UTF-8 replacement character `EF BF BD`, annotated as `/* -1 */` for unassigned/non-mappable positions.
- A small five-row private-use run appears near the end with `EE A0 90` through `EE A0 94`.
- The final row is `EF BF BD` with the comment `Hold entry for non-identical convsersion.`

The mapping starts with GB2312 symbol/punctuation-style entries, including ideographic punctuation, math symbols, fullwidth ASCII, kana, Greek/Cyrillic, pinyin/Bopomofo, and box drawing. The bulk of the file is CJK ideograph mappings encoded as UTF-8 triples.

## Control Flow

There is no executable control flow in this file. Runtime conversion behavior is entirely data-driven:

1. External kernel iconv code validates and normalizes GB2312 input.
2. It indexes into `kiconv_gb2312_utf8`.
3. It copies the resulting UTF-8 bytes to the destination buffer.
4. Missing or non-identical mappings are represented by replacement-character rows in this table.

Error handling, incomplete multibyte sequence handling, and output-buffer checks are not implemented here.

## Dependencies

The file assumes kernel/system typedefs are already available, especially `uchar_t`. It does not include headers directly.

Related integration points visible in the source tree:

- `uts/common/sys/Makefile` lists `kiconv_gb2312_utf8.h` among exported/generated kiconv headers.
- Adjacent CCK/kiconv headers provide related Chinese conversion tables and byte validation logic.
- Direct textual references to `kiconv_gb2312_utf8` outside this header were not found in the scanned tree, suggesting inclusion may be generated, indirect, or limited to build-specific conversion units.

## Risks And Invariants

Important invariants:

- `KICONV_GB2312_UTF8_MAX` must equal the initializer count.
- Replacement rows are meaningful placeholders and must not be removed just because they look repetitive.
- Two-byte UTF-8 rows depend on zero-filled padding.
- Table order and indexing convention must remain aligned with the consumer’s GB2312 index calculation.

Risks:

- Manual edits are high risk because semantic correctness depends on thousands of table entries.
- Because the array is `static` in a header, each including translation unit receives its own copy.
- The file does not self-describe valid GB2312 byte ranges; callers must perform validation elsewhere.
- The final “non-identical conversion” hold entry is part of the table contract and should be preserved even though it is not a normal character mapping.
