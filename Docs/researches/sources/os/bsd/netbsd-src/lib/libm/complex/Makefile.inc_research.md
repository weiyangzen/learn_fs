# File Research: sources/os/bsd/netbsd-src/lib/libm/complex/Makefile.inc

## Scope

Build recipe for NetBSD libm complex-number sources and manual-page links.

## APIs And Behavior

- Adds `.PATH` to `${.CURDIR}/complex`.
- `COMPLEX_SRCS` includes core C99 complex functions and helper implementations, including `catrig.c`.
- For each core source, builds double, float, and long-double variants by filename substitution.
- Adds man pages and manpage links for public functions, excluding `catrig*` and `cephes_*`.
- `CATRIG_SRCS` lists legacy inverse trig wrapper names and only adds their long-double variant sources plus manpage links.

## Dependencies And Risks

- Build output can differ from the source files present: double/float inverse trig symbols come from `catrig.c` / `catrigf.c`, while some older standalone source files are still present in the tree.
