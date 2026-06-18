# File Research: sources/os/bsd/netbsd-src/lib/libc/gdtoa/arithchk.c

Standalone generator/check program that deduces floating-point arithmetic properties for gdtoa's `arith.h`. It tests the binary representation of `1e13` through unions using `long`, `int`, or `long`-sized double layouts to identify IEEE little-endian, IEEE big-endian, VAX, IBM, or Cray formats.

`Lcheck`, `icheck`, and `ccheck` perform representation checks and detect double alignment padding. `fzcheck` detects sudden underflow by repeated squaring. `main` writes preprocessor defines to stdout or `arith.h` when `WRITE_ARITH_H` is set, including arithmetic kind, `Long int` override, `Intcast`, `Double_Align`, `X64_bit_pointers`, `NO_LONG_LONG`, and `Sudden_Underflow` as applicable.

Dependencies: standard I/O only; used as a build/configuration tool rather than libc runtime code.

Risks/invariants: relies on type-punning through unions and magic representation constants. Unknown formats emit a comment and exit nonzero.
