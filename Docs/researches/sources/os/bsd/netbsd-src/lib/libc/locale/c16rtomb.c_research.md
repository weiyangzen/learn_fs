# File Research: sources/os/bsd/netbsd-src/lib/libc/locale/c16rtomb.c

Read completely: 212 lines.

This file implements `c16rtomb` and `c16rtomb_l`, converting UTF-16 code units to the current locale's multibyte encoding. It stores pending high surrogates in a private state embedded in `mbstate_t`, combines valid surrogate pairs into a UTF-32 scalar, and delegates scalar output to `c32rtomb_l`.

Important interactions: uses `c32rtomb.h` to assert state-size compatibility and `setlocale_local.h` for `_current_locale()`. Null `ps` uses a static state as required by the C API, and null `s` emits a reset/null conversion into a local buffer.

Security/reliability notes: invalid surrogate ordering sets `errno = EILSEQ`. A null code unit discards any pending high surrogate and resets through `c32rtomb_l`. Static state for null `ps` is not thread-safe by standard allowance.
