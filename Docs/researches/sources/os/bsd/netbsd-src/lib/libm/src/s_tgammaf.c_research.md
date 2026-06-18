# File Research: sources/os/bsd/netbsd-src/lib/libm/src/s_tgammaf.c

Implements `tgammaf()` by calling double-precision `tgamma()` and casting the result to float. The file explicitly avoids a float-specialized implementation because the gamma function grows too quickly for float range to make a dedicated version worthwhile.

Important dependency: `<math.h>`.

Behavior and exceptions are inherited from `tgamma()`, with final narrowing to float.
