<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/xlat/cacheflush_flags.in -->
# sources/test-tools/strace/src/xlat/cacheflush_flags.in

Purpose: Declarative xlat input table `cacheflush_flags` for strace generated headers; it maps kernel/API numeric constants to printable symbolic names used by decoders.

Important APIs/types/functions:
- Contains 11 constant rows, including `FLUSH_CACHE_BOTH	3`
- Representative constants: `FLUSH_CACHE_BOTH`, `FLUSH_CACHE_DATA`, `FLUSH_CACHE_INSN`, `BCACHE`, `ICACHE`, `DCACHE`, `BCACHE`, `ICACHE`, `DCACHE`, `CACHEFLUSH_D_INVAL`...
- Generator directives/preprocessor guards: `#From arch/arc/include/uapi/asm/cachectl.h`, `#From arch/m68k/include/uapi/asm/cachectl.h`, `#From arch/sh/include/uapi/asm/cachectl.h`, `#if defined M68K`, `#elif defined BFIN || defined CSKY`, `#elif defined SH`, `#endif`

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
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/xlat/cacheflush_flags.in -->
