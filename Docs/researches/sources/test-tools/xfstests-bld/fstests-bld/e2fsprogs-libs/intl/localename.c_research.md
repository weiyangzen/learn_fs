# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/intl/localename.c

Purpose: determines the active gettext locale name in XPG syntax for message lookup. On POSIX-like builds `_nl_locale_name(category, categoryname)` returns `setlocale(category, NULL)` when reliable, otherwise follows the environment precedence `LC_ALL`, category-specific variable, then `LANG`, defaulting to `"C"`.

Important APIs and control flow: the only exported routine is `_nl_locale_name`. Non-Win32 control flow is intentionally small and returns pointers owned by libc/environment/static storage. The large Win32 branch first honors POSIX-style environment overrides, then reads `GetThreadLocale()`, strips sort rules with `LANGIDFROMLCID`, splits `PRIMARYLANGID` and `SUBLANGID`, and maps many Windows language/sublanguage constants to gettext locale strings such as `en_US`, `pt_BR`, or modifiers like `az_AZ@cyrillic`.

State and dependencies: no persistent state is stored. Dependencies are `stdlib.h`, `locale.h`, optional `windows.h`, configure macros, and platform locale constants, with fallback definitions for older MinGW headers.

Integration points: called by gettext lookup code to choose catalog directories. It integrates with `LC_MESSAGES` category naming and Win32 process/thread locale APIs.

Risks and test signals: risks are stale or ambiguous Win32 mappings, environment lifetime assumptions, and codeset omission. Test by overriding `LC_ALL`, category variables, and `LANG`; on Windows test representative LCIDs and fallback `"C"`.
