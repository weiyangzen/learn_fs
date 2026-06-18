# sources/test-tools/fio/oslib/strcasestr.h

Purpose: declaration for fallback `strcasestr()`.

Important APIs/types: declares `char *strcasestr(const char *haystack, const char *needle)` when `CONFIG_STRCASESTR` is absent.

Control flow and state: no implementation or state.

Dependencies and integration: paired with `strcasestr.c`; avoids declaring the function when libc already provides it.

Risks: configuration must match platform headers to avoid duplicate declarations.

Test signals: compile on platforms with and without native `strcasestr()`.
