# File Research: sources/os/bsd/netbsd-src/lib/libc/regex/regfree.c

Implements `regfree()`. It validates regex magic, marks both public and guts structures invalid, and frees all compiler allocations: strip, cset ranges/wides/types, cset array, mandatory literal string, Boyer-Moore jump tables, and `re_guts`.

A notable detail is freeing `charjump` with `free(&g->charjump[CHAR_MIN])` because `regcomp.c` shifts the stored pointer to allow signed-char indexing.
