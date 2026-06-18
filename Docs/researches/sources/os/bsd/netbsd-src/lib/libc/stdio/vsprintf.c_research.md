# File Research: sources/os/bsd/netbsd-src/lib/libc/stdio/vsprintf.c

Read completely: 113 lines.

Implements `vsprintf_l()`, `vsprintf()`, `sprintf_l()`, and `sprintf()`. The core builds a temporary string-backed `FILE` with `__SWR | __SSTR`, points its buffer at the caller-provided destination, gives it `INT_MAX` capacity, and delegates formatting to `__vfprintf_unlocked_l()`.

Locale-aware variants accept an explicit `locale_t`; ordinary variants use `_current_locale()`. Because this is `sprintf`, no real destination bound is enforced beyond the artificial `INT_MAX`, so caller buffer sizing remains the safety boundary.
