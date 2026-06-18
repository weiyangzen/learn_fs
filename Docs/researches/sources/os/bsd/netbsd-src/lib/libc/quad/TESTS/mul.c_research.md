# File Research: sources/os/bsd/netbsd-src/lib/libc/quad/TESTS/mul.c

Interactive test driver for `__muldi3()`. It reads two 64-bit values as high/low 32-bit words in decimal or hex, invokes the quad multiply helper, and prints the product.

Like `divrem.c`, this is a historical manual diagnostic program with old-style `main()` and target-layout assumptions. It is useful for spot-checking the low-level multiplication routine but not a portable automated test.
