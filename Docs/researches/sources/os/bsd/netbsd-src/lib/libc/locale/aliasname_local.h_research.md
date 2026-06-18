# File Research: sources/os/bsd/netbsd-src/lib/libc/locale/aliasname_local.h

Read completely: 74 lines.

This header declares `__unaliasname` and defines inline `__isforcemapping`, which recognizes the case-insensitive literal `/FORCE` without using locale-sensitive string comparison.

Important interactions: `nb_lc_template.h` uses these helpers while resolving locale aliases from `locale.alias`, distinguishing force mappings from ordinary alias fallback behavior.

Security/reliability notes: `__isforcemapping` indexes fixed positions in `name` and assumes a valid NUL-terminated string. It intentionally avoids `strcasecmp` because locale lookup must not depend on the current locale.
