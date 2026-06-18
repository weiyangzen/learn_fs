# File Research: sources/os/bsd/netbsd-src/lib/libc/string/bm.c

Implements the `bm(3)` Boyer-Moore pattern API: `bm_comp()`, `bm_exec()`, and `bm_free()`. `bm_comp()` copies the pattern, builds a 256-entry bad-character delta table, chooses a rare guard character using either a caller frequency table or the built-in English-ish default, and computes the secondary match shift.

`bm_exec()` searches a byte buffer with a fast skip loop, guard check, forward verification, and fallback slow loop near the end. `bm_free()` releases the pattern, delta table, and descriptor.
