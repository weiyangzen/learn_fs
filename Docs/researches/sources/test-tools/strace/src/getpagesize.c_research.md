# sources/test-tools/strace/src/getpagesize.c

Decoder for `getpagesize`, a no-argument pure syscall/library-entry style decoder. It prints no arguments and relies on the generic return value for the page size. There is no state or dependency beyond `defs.h`. Risks are minimal; the decoder must not invent arguments or mark the return incorrectly. Tests should verify traces show an empty argument list and decimal return value.
