# File Research: sources/os/bsd/netbsd-src/lib/libc/regex/utils.h

Utility header for regex internals. It abstracts wide-character support under `NLS`; without NLS it defines lightweight stand-ins for `wint_t`, `mbstate_t`, `wctype_t`, wide case/class functions, and declares local `__regex_wctype()` / `__regex_iswctype()`.

It defines duplication limits, character-domain constants (`NC_MAX`, `NC`), unsigned character typedef `uch`, assertion behavior tied to `REDEBUG`, and a compatibility mapping from `memmove()` to `bcopy()` under `USEBCOPY`.

This header keeps the regex implementation buildable in libc and host-tool contexts.
