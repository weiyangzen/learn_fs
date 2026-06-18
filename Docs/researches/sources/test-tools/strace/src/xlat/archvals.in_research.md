<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/xlat/archvals.in -->
# sources/test-tools/strace/src/xlat/archvals.in

Purpose: Declarative xlat input table `archvals` for strace generated headers; it maps kernel/API numeric constants to printable symbolic names used by decoders.

Important APIs/types/functions:
- Contains 23 constant rows, including `ARCH_SET_GS			0x1001`
- Representative constants: `ARCH_SET_GS`, `ARCH_SET_FS`, `ARCH_GET_FS`, `ARCH_GET_GS`, `ARCH_GET_CPUID`, `ARCH_SET_CPUID`, `ARCH_GET_XCOMP_SUPP`, `ARCH_GET_XCOMP_PERM`, `ARCH_REQ_XCOMP_PERM`, `ARCH_GET_XCOMP_GUEST_PERM`...
- Generator directives/preprocessor guards: `#sorted`, `#From arch/x86/include/uapi/asm/prctl.h`, `#Prefix ARCH_`

Control flow:
- `src/xlat/gen.sh` reads this `.in` file and emits a generated `xlat/*.h` table consumed by decoder `printxval`/`printflags` calls
- row order and directives determine whether the generated table is normal, sorted, indexed, macro-only, conditional, or enum-backed

State and persistence behavior:
- no runtime mutable state in this file; values become compiled static `struct xlat` data after generation
- persistence is source-controlled constant metadata aligned with Linux/uapi headers and portability guards

Dependencies and integration points:
- depends on the referenced kernel/libc macro names being available or supplied with fallback numeric definitions by the generator
- integrates with decoders that include the generated header and with `xlat.c` lookup/printing routines

Risks:
- wrong numeric fallback, stale macro coverage, or misordered `#sorted` entries can produce incorrect symbolic decoding
- conditional rows need architecture and kernel-header coverage so missing macros degrade predictably rather than breaking builds

Test signals:
- test signals are generated-header build success, static assertions from `gen.sh`, and strace output tests that verify symbolic names for known values plus raw fallback for unknown bits
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/xlat/archvals.in -->
