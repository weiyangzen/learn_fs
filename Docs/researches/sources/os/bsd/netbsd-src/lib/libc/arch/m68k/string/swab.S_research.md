# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/m68k/string/swab.S

This file implements `swab`, copying pairs of bytes from source to destination with each pair swapped. It converts the byte count to a word count, ignores any odd trailing byte, then loops over word-sized swaps.

On ordinary m68k it loads a word, rotates it by 8 bits, and stores it; on ColdFire it performs two byte loads/stores manually. The semantics are the traditional BSD/POSIX `swab` behavior.
