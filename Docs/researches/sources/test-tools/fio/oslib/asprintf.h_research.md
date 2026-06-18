# sources/test-tools/fio/oslib/asprintf.h

Purpose: conditional declarations for fio's `asprintf()`/`vasprintf()` fallbacks.

Important APIs/types: includes `<stdarg.h>` and declares `vasprintf()` when `CONFIG_HAVE_VASPRINTF` is absent and `asprintf()` when `CONFIG_HAVE_ASPRINTF` is absent.

Control flow and state: no logic or state.

Dependencies and integration: paired with `oslib/asprintf.c`; consumers include this header to get portable declarations without conflicting with libc-provided functions.

Risks: configuration macros must match the platform headers and build objects, or duplicate/missing declarations can occur.

Test signals: configure/build matrix on platforms with and without GNU `asprintf()`.
