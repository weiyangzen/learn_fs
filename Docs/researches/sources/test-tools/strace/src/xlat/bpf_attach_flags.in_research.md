<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/xlat/bpf_attach_flags.in -->
# sources/test-tools/strace/src/xlat/bpf_attach_flags.in

Purpose: Declarative xlat input table `bpf_attach_flags` for strace generated headers; it maps kernel/API numeric constants to printable symbolic names used by decoders.

Important APIs/types/functions:
- Contains 8 constant rows, including `BPF_F_ALLOW_OVERRIDE	1U`
- Representative constants: `BPF_F_ALLOW_OVERRIDE`, `BPF_F_ALLOW_MULTI`, `BPF_F_REPLACE`, `BPF_F_BEFORE`, `BPF_F_AFTER`, `BPF_F_ID`, `BPF_F_PREORDER`, `BPF_F_LINK`
- Generator directives/preprocessor guards: `#From include/uapi/linux/bpf.h`, `#Prefix BPF_F_`

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
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/xlat/bpf_attach_flags.in -->
