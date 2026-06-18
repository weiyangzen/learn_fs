# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/std.h

Main standard definitions header for Ghostscript code.

Key points:
- Includes `stdpre.h` and generated `arch.h`.
- Defines lower-case compatibility aliases for architecture macros.
- Computes memory alignment requirements and type sizes.
- Defines `bits16`, `bits32`, signed/unsigned min/max constants, pointer min/max, and reliable arithmetic right shift macros.
- Declares Ghostscript output routing functions: `outwrite`, `errwrite`, `outflush`, `errflush`, `outprintf`, and `errprintf`.
- Defines `dprintf*`, `dlprintf*`, `eprintf*`, and `lprintf*` debugging/error-printing macro families.
- Declares program identification helpers and module init-proc macro.

Dependencies and interactions:
- Depends on `arch.h` for target layout/endian/compiler behavior.
- Exposes `gs_memory_t` as a forward type because output routing is memory-context aware.
- Used broadly across Ghostscript source before platform and system headers.

Research relevance:
- This is the central Ghostscript portability and diagnostics contract.
