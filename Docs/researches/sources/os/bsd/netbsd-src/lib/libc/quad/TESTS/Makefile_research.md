# File Research: sources/os/bsd/netbsd-src/lib/libc/quad/TESTS/Makefile

Simple historical test Makefile building two interactive test programs: `mul` from `mul.c` plus `../muldi3.c`, and `divrem` from `divrem.c` plus `../qdivrem.c`.

It invokes `gcc -g -DSPARC_XXX` directly and is not integrated with modern NetBSD ATF test infrastructure. Its purpose is manual/local validation of quad multiplication and division/reminder helper behavior.
