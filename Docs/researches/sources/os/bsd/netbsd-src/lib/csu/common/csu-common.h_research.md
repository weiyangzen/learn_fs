# File Research: sources/os/bsd/netbsd-src/lib/csu/common/csu-common.h

Common CSU declarations. It defines a `__common` macro using the compiler `__common__` attribute when available, because historical symbols are defined both in libc and CSU.

It declares common `__progname`, `environ`, `__ps_strings`, and `_libc_init()` with constructor/used attributes.
