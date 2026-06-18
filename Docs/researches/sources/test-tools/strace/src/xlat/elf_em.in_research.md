<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/xlat/elf_em.in -->
# sources/test-tools/strace/src/xlat/elf_em.in

Purpose: Declarative xlat input table `elf_em` for strace generated headers; it maps kernel/API numeric constants to printable symbolic names used by decoders. File comments/directives provide context such as: See also https://www.sco.com/developers/gabi/latest/ch4.eheader.html EM_IAMCU		6 - Intel MCU

Important APIs/types/functions:
- Contains 188 constant rows, including `EM_NONE			0`
- Representative constants: `EM_NONE`, `EM_M32`, `EM_SPARC`, `EM_386`, `EM_68K`, `EM_88K`, `EM_486`, `EM_860`, `EM_MIPS`, `EM_S370`...
- Generator directives/preprocessor guards: `#sorted`, `#From include/uapi/linux/elf-em.h`, `#Prefix EM_`

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
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/xlat/elf_em.in -->
