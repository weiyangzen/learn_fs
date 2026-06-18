# File Research: sources/os/bsd/netbsd-src/lib/libc/locale/_wcstoul.h

Read completely: 137 lines.

This template implements unsigned wide-string integer conversion for `wcstoul`, `wcstoull`, and `wcstoumax`. It validates base, skips whitespace, accepts optional sign and prefixes, accumulates unsigned values with overflow checks, and applies negation after parsing if a leading minus was present.

Important interactions: concrete wrappers define `_FUNCNAME`, `__UINT`, and `__UINT_MAX`. It shares digit conversion via `__wctoint.h` and locale retrieval via `setlocale_local.h`.

Security/reliability notes: overflow saturates to `__UINT_MAX` and sets `ERANGE`; invalid base sets `EINVAL`. Negative inputs are accepted by unsigned conversion semantics and wrapped after successful parse.
