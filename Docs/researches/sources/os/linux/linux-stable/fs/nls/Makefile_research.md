# File Research: sources/os/linux/linux-stable/fs/nls/Makefile

## Purpose
Maps NLS Kconfig symbols to object files built by Kbuild.

## Main Mappings
- `CONFIG_NLS` builds `nls_base.o`.
- DOS/Windows codepages map to `nls_cp*.o`, with some configs producing multiple objects:
  - `CONFIG_NLS_CODEPAGE_932` builds `nls_cp932.o` and `nls_euc-jp.o`.
  - `CONFIG_NLS_KOI8_U` builds `nls_koi8-u.o` and `nls_koi8-ru.o`.
- ISO variants map to `nls_iso8859-*.o`, except `CONFIG_NLS_ISO8859_8` builds `nls_cp1255.o`.
- Mac codepage symbols map directly to `mac-*.o`.

## Relevant Mappings for This Group
- `CONFIG_NLS_MAC_CELTIC` -> `mac-celtic.o`
- `CONFIG_NLS_MAC_CENTEURO` -> `mac-centeuro.o`
- `CONFIG_NLS_MAC_CROATIAN` -> `mac-croatian.o`
- `CONFIG_NLS_MAC_CYRILLIC` -> `mac-cyrillic.o`
- `CONFIG_NLS_MAC_GAELIC` -> `mac-gaelic.o`

## Research Notes
The Makefile is purely declarative Kbuild wiring. It is the bridge from the `Kconfig` tristates to the generated charset modules’ object files.
