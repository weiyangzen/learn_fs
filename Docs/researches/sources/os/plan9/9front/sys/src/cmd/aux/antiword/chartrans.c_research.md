# File Research: sources/os/plan9/9front/sys/src/cmd/aux/antiword/chartrans.c

Character translation module for Antiword. It maps Word/DOS/Windows/Mac/Unicode characters to local output encodings or simplified representations.

Important behavior:
- Contains built-in codepage tables for CP850, CP1250, CP1251, CP1252, MacRoman, and Microsoft private-use Symbol area mappings.
- `bReadCharacterMappingTable()` reads external mapping files of local byte to Unicode mappings, validates them, stores relevant entries, and sorts for binary search.
- `ulTranslateCharacters()` normalizes Word characters, handles Word control/special characters, note markers, bullets, dashes, quotes, spaces, arrows, ligatures, Euro sign, and UTF-8 passthrough.
- Provides special mappings for PostScript/PDF Latin-1 output to improve typography.
- `ucGetBulletCharacter()` and `ucGetNbspCharacter()` retrieve local printable equivalents.
- `ulToUpper()` performs locale-independent uppercase conversion for ASCII, Latin-1, and optionally ISO-10646 wchar platforms.

Filesystem relevance:
- Transforms bytes read from Word/OLE streams into stable output text/markup encodings.
