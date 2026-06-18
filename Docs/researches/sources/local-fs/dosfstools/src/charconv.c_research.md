# File Research: sources/local-fs/dosfstools/src/charconv.c

DOS OEM codepage conversion layer for short names and labels.

Main behavior:
- Provides an internal CP850 Unicode table and transliteration table.
- With `HAVE_ICONV`:
  - Initializes conversions between DOS codepage and local charset.
  - Initializes conversions between DOS codepage and `WCHAR_T`.
  - Falls back to the internal CP850 table when iconv cannot initialize CP850.
- Without `HAVE_ICONV`:
  - Supports only CP850 through internal conversion functions.
- Public functions:
  - `set_dos_codepage()`
  - `dos_char_to_printable()`
  - `local_string_to_dos_string()`
  - `dos_string_to_wchar_string()`
  - `wchar_string_to_dos_string()`

Error handling:
- Reports conversion failures, too-long strings, and illegal input sequences to `stderr`.
- Returns `0` on conversion failure and nonzero on success.

Consumers:
- `file.c` uses printable conversion for short filenames.
- `boot.c`, `fatlabel.c`, and `check.c` use it for volume labels.
- `common.c` uses wchar conversion to validate lowercase label characters independent of the raw DOS codepage.

Research notes:
- The conversion state is process-global and initialized once.
- Label length enforcement is partly done before conversion and partly by conversion output buffer sizing.
