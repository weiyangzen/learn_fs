# File Research: sources/windows/reactos/drivers/filesystems/ext2/src/nls/nls_euc-jp.c

Purpose: Linux-style NLS converter for Japanese EUC-JP in the ReactOS Ext2 source tree. Unlike the single-byte generated table files, this module loads the existing `cp932` NLS table and translates between Unicode and CP932/Shift-JIS first, then between Shift-JIS and EUC-JP.

Core structures and data:
- `static struct nls_table *p_nls` stores the loaded `cp932` backend.
- Macros classify Shift-JIS low bytes, JIS X 0208, JIS X 0201 kana, user-defined character ranges, IBM extended ranges, and NEC/IBM extension ranges.
- Macros classify EUC bytes, SS2 kana sequences, SS3 G3 sequences, and low/high user-defined ranges.
- `MAP_SJIS2EUC` and `MAP_EUC2SJIS` implement arithmetic conversion between the normal JIS X 0208 / UDC Shift-JIS and EUC coordinate systems.
- `sjisibm2euc_map` maps CP932 IBM extended byte pairs to EUC-JP two- or three-byte sequences.
- `euc2sjisibm_jisx0212_map` and `euc2sjisibm_g3upper_map` provide reverse lookup for IBM extended characters that cannot be converted by the simple arithmetic macros.

Important helper behavior:
- `sjisibm2euc()` converts IBM Shift-JIS extensions to EUC. Some entries become two-byte JIS X 0208 EUC sequences; others are emitted as SS3 plus two bytes.
- `euc2sjisibm_jisx0212()` binary-searches a sorted EUC-to-IBM map and returns a CP932 pair when found.
- `euc2sjisibm_g3upper()` maps upper G3 EUC extension blocks to CP932 extension pairs by computed index.
- `euc2sjisibm()` tries G3 upper mapping first, then the JIS X 0212 map.
- `sjisnec2sjisibm()` normalizes NEC/IBM Shift-JIS extension ranges into IBM extension byte pairs before EUC conversion.

Important conversion behavior:
- `uni2char()` first calls `p_nls->uni2char()` to encode Unicode as CP932/Shift-JIS.
- One-byte CP932 halfwidth kana `0xA1..0xDF` is rewritten as EUC SS2 followed by the kana byte, requiring two output bytes.
- Two-byte CP932 is converted by category: NEC/IBM normalization, UDC low arithmetic conversion, UDC high SS3 conversion, IBM extension map conversion, or normal JIS X 0208 arithmetic conversion.
- Invalid or unsupported CP932 results return `-EINVAL`; insufficient output room returns `-ENAMETOOLONG`.
- `char2uni()` parses EUC-JP into a temporary two-byte Shift-JIS buffer, then delegates Unicode conversion to `p_nls->char2uni()`.
- `char2uni()` handles ASCII/JIS X 0201 romaji as one byte, SS2 kana as two bytes, normal JIS X 0208 as two bytes, low UDC as two bytes, and SS3 high UDC/IBM extensions as three bytes.
- Unsupported JIS X 0212 or invalid SS3 sequences return `-EINVAL`; a commented-out GETA fallback is intentionally disabled.

Dependencies and interfaces:
- `init_nls_euc_jp()` loads `cp932` with `load_nls("cp932")`, copies its upper/lower case tables into this module's `table`, and registers charset `"euc-jp"`.
- `exit_nls_euc_jp()` unregisters the EUC-JP table and unloads the CP932 backend.
- The module has no alias and no standalone Unicode mapping tables for general characters; CP932 is a hard runtime dependency.

Design notes and risks:
- Failure to load `cp932` makes initialization return `-EINVAL`, so EUC-JP availability depends on the CP932 NLS module.
- The mapping helpers are dense and byte-arithmetic-heavy. Range macro correctness is critical because helper functions assume callers have classified bytes before indexing generated maps.
- `sjisibm2euc()` computes an index from Shift-JIS bytes; callers must only pass bytes satisfying `IS_SJIS_IBM`.
- `char2uni()` returns `-EINVAL` for truncated multibyte EUC input, while the single-byte generated modules generally have no comparable input-length checks.
- The public case tables are borrowed from CP932, so case behavior follows the backend rather than a separate EUC-specific table.
- Correctness is filename-critical: errors can make Japanese names fail lookup, fail round trip, or collide after conversion.
