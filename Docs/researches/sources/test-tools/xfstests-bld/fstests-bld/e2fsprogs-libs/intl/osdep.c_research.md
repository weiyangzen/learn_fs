# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/intl/osdep.c

Purpose: selects OS-dependent libintl glue at compile time.

Important APIs and control flow: if `__EMX__` is defined, the file includes `os2compat.c` directly so OS/2 support is compiled into this translation unit. Otherwise it declares `typedef int dummy;` only to keep compilers from warning about an empty translation unit.

State and persistence: no state outside what `os2compat.c` contributes on OS/2.

Dependencies and integration: this file is part of the libintl build list and provides a stable platform hook without requiring every makefile to conditionally add OS/2 sources.

Risks and test signals: including a `.c` file is intentional here but can surprise tooling. Test that non-OS/2 builds compile without symbols, and OS/2 builds include exactly one copy of the compatibility globals and constructor.
