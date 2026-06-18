# File Research: sources/os/linux/linux/fs/nls/Makefile

Maps NLS Kconfig symbols to build objects.

Main responsibilities:
- Builds `nls_base.o` when `CONFIG_NLS` is enabled.
- Maps DOS/Windows, ISO-8859, KOI8, UTF-8, UCS2, and Macintosh charset options to object files.
- Some config symbols build multiple objects, such as CP932 also building `nls_euc-jp.o`, and KOI8-U also building `nls_koi8-ru.o`.

Mac mappings relevant to this group:
- `CONFIG_NLS_MAC_CELTIC` -> `mac-celtic.o`
- `CONFIG_NLS_MAC_CENTEURO` -> `mac-centeuro.o`
- `CONFIG_NLS_MAC_CROATIAN` -> `mac-croatian.o`
- `CONFIG_NLS_MAC_CYRILLIC` -> `mac-cyrillic.o`
- `CONFIG_NLS_MAC_GAELIC` -> `mac-gaelic.o`

Risk notes:
- The Makefile is straightforward object selection; the main maintenance risk is keeping symbol names aligned with Kconfig and module charset names.
