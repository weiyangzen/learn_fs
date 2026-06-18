# File Research: sources/os/bsd/netbsd-src/lib/libform/type_alpha.c

Defines builtin `TYPE_ALPHA`.

It mirrors `TYPE_ALNUM` but accepts alphabetic characters only. The field validator trims leading/trailing blanks, rejects empty input, checks that the alphabetic span is no longer than the configured width, rejects any non-blank trailing data, and writes the normalized value back to buffer 0.

Character validation uses `isalpha`.
