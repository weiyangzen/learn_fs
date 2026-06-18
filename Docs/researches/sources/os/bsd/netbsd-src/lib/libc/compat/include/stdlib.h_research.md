# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/include/stdlib.h

Declares assorted compatibility stdlib APIs.

It includes old and modern variants for `unsetenv`, `putenv`, `devname`, `initstate`, and `srandom`, preserving historical argument types such as `int32_t dev` and `unsigned long` seeds.

Filesystem relevance is direct for `devname`, which maps device numbers to names.
