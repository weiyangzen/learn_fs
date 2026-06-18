# File Research: sources/os/linux/linux/fs/nls/Kconfig

Defines kernel configuration for Native Language Support.

Main responsibilities:
- Provides `menuconfig NLS`, building `nls_base` as built-in or module.
- Defines `NLS_DEFAULT`, defaulting to `iso8859-1`, with a list of accepted charset names.
- Exposes DOS/Windows codepages, ISO-8859 variants, KOI8 variants, ASCII, UTF-8, UCS2 utilities, and Macintosh codepages.
- Describes intended filesystem consumers, especially FAT/Joliet/NT/BEOS/NCP/SMB and HFS-family filesystems.

Mac options covered by this group:
- `NLS_MAC_CELTIC`: `macceltic`.
- `NLS_MAC_CENTEURO`: `maccenteuro`.
- `NLS_MAC_CROATIAN`: `maccroatian`.
- `NLS_MAC_CYRILLIC`: `maccyrillic`.
- `NLS_MAC_GAELIC`: `macgaelic`.

Dependencies and build linkage:
- This file only declares configuration symbols.
- Actual object selection is in `fs/nls/Makefile`.

Risk notes:
- Many help texts still use older filesystem wording and recommend `Y` for several legacy codepages.
- `NLS_ISO8859_8` builds CP1255 in the Makefile, which is intentional in this tree but non-obvious from the symbol name.
