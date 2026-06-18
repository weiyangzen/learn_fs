# File Research: sources/os/plan9/9front/sys/src/cmd/aux/antiword/options.c

Runtime option parser and character mapping file loader for Antiword.

Key responsibilities:
- Holds current options with defaults for paragraph width, conversion type, removed/hidden text handling, encoding, page size, image level, and RISC OS scale settings.
- Defines known paper sizes for PostScript/PDF output.
- Resolves mapping files from `ANTIWORDHOME`, `$HOME/.antiword`, and the global Antiword directory, adding `.txt` when needed.
- Maps selected mapping files to coarse encodings: Latin-1, Latin-2, Cyrillic, and UTF-8.
- Parses non-RISC OS CLI flags for landscape, paper size, formatted text, image handling, mapping file, PostScript/PDF, raw text, width, and XML DocBook output.
- Contains RISC OS choices-file and GUI event handling under `__riscos`.

Dependencies:
- Uses `getopt`, environment variables, Antiword mapping-table reader, output conversion enums, and RISC OS Wimp APIs when enabled.

Notable risks:
- Mapping filename storage is capped at 32 characters plus suffix.
- PDF/PostScript explicitly reject UTF-8; PDF also rejects Cyrillic.
- Option state is global, so callers rely on `iReadOptions()` before output creation.
