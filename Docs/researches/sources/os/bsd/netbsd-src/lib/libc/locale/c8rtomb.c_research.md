# File Research: sources/os/bsd/netbsd-src/lib/libc/locale/c8rtomb.c

Read completely: 228 lines.

This file implements `c8rtomb` and `c8rtomb_l`, converting UTF-8 code units to the current locale's multibyte encoding. It maintains a compact UTF-8 DFA state and partial scalar buffer inside `mbstate_t`; incomplete byte sequences produce no output until a complete scalar is accepted, then output is delegated to `c32rtomb_l`.

Important interactions: uses a locally defined class/state table inspired by Hoehrmann's UTF-8 decoder, plus `c32rtomb.h` for state-size assertions. Null `s` resets through a null code unit conversion.

Security/reliability notes: invalid UTF-8 transitions return `(size_t)-1` with `EILSEQ`. A null byte discards buffered UTF-8 input and emits a null scalar. Static state for null `ps` is allowed but not race-free.
