# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/intl/os2compat.h

Purpose: centralizes OS/2 compile-time compatibility macros for gettext.

Important APIs/types/functions: when not included from the OS/2 implementation itself, it remaps `LIBDIR`, `LOCALEDIR`, and `LOCALE_ALIAS_PATH` to runtime globals `_nlos2_libdir`, `_nlos2_localedir`, and `_nlos2_localealiaspath`. It declares those globals, maps `strcasecmp`/`strncasecmp` to `stricmp`/`strnicmp`, forces `HAVE_STRCASECMP`, remaps `getenv` to `_nl_getenv`, and defines legacy `LC_MESSAGES_COMPAT`.

State and persistence: the header declares external path globals owned by `os2compat.c`; it stores no state itself.

Dependencies and integration: intended for inclusion from `config.h` or OS/2-aware gettext compilation units. It changes names globally, so include order matters.

Risks and test signals: broad macro replacement can affect unrelated code included afterward. Test OS/2 builds for correct path macros, case-insensitive alias lookup, and compatibility with older gettext `LC_MESSAGES == -1` assumptions.
