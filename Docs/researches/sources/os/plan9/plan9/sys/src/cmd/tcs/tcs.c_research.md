# File Research: sources/os/plan9/plan9/sys/src/cmd/tcs/tcs.c

Main driver and central charset registry for Plan 9 `tcs`, a text character-set converter.

Key responsibilities:
- Parses `-c`, `-f`, `-l`, `-s`, `-t`, and `-v`.
- Selects input and output converters through `conv()`.
- Reads stdin or named files, then dispatches to table-based or function-based input conversion.
- Maintains global conversion accounting: input bytes, output bytes, runes, and errors.
- Implements UTF-16/native, UTF-16BE, UTF-16LE input and output helpers.
- Implements generic 8-bit table input and table output, including reverse-map construction.
- Defines built-in maps for ASCII, legacy MS-DOS variants, and the `convert[]` registry covering ISO-8859, JIS, Big5, GB, Korean, UTF, Unicode, Windows code pages, Tamil TUNE, Cyrillic variants, HTML, and aliases.

Important behavior:
- `clean` drops unmappable or malformed input; otherwise bad data maps to `BADMAP` or `Runeerror`.
- `squawk` controls diagnostics, while verbose mode forces diagnostics and prints counts.
- UTF-16 native mode handles BOM and byte swapping; BE/LE modes force byte order.
- Table output rebuilds the reverse Unicode-to-byte table on each call.

Notable risks:
- Many converter implementations are referenced externally, so the registry is a hard compatibility surface.
- Table output assumes `NRUNE` indexing covers all mapped runes.
- Native `unicode_out()` writes host-endian `Rune` values and a BOM, matching historical Plan 9 assumptions rather than modern UTF-16 portability expectations.
