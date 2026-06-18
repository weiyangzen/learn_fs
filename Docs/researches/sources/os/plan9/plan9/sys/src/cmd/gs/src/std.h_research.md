# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/std.h

Purpose: central Ghostscript standard header that layers architecture-dependent constants from `arch.h` on top of compiler portability definitions from `stdpre.h`.

Key contents:
- Maps upper-case `ARCH_*` values to older lower-case compatibility names.
- Defines memory alignment, integer sizes, small-memory detection, `bits16`/`bits32`, signed min/max values, unsigned max aliases, and pointer min/max values.
- Provides portable arithmetic right-shift macros based on `arch_arith_rshift`.
- Declares Ghostscript output/error functions: `outwrite`, `errwrite`, `outflush`, `errflush`, `outprintf`, `errprintf`.
- Defines extensive debug/error printing macro families: `dprintf*`, `dlprintf*`, `eprintf*`, `lprintf*`.
- Declares program identity helpers and repeats `gs_memory_t`/`init_proc` compatibility definitions.

Dependencies: includes `stdpre.h`, `arch.h`, and `<stdio.h>`.

Integration notes: almost every C file in this group depends indirectly on this header for `byte`, `uint`, `bool`, `private`, `public`, architecture constants, and diagnostic output.

Risks: heavy macro use makes side effects possible in printf-like wrappers; duplicated `gs_memory_t`/`init_proc` definitions are guarded but reflect legacy layering.
