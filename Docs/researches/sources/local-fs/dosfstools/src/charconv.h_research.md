# File Research: sources/local-fs/dosfstools/src/charconv.h

Header for DOS/local/wide-character conversion helpers.

Contents:
- Defines `DEFAULT_DOS_CODEPAGE` as 850.
- Declares public conversion functions:
  - `set_dos_codepage`
  - `dos_char_to_printable`
  - `local_string_to_dos_string`
  - `dos_string_to_wchar_string`
  - `wchar_string_to_dos_string`

Role:
- Centralizes codepage handling for labels and FAT short-name display.
