<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/xlat/compat_ptrace_cmds.in -->
# sources/test-tools/strace/src/xlat/compat_ptrace_cmds.in

Purpose: Declarative xlat input table `compat_ptrace_cmds` for strace generated headers; it maps kernel/API numeric constants to printable symbolic names used by decoders. File comments/directives provide context such as:  These two are not defined in arch/arm64/include/asm/ptrace.h,

Important APIs/types/functions:
- Contains 10 constant rows, including `COMPAT_PTRACE_GETREGS		12`
- Representative constants: `COMPAT_PTRACE_GETREGS`, `COMPAT_PTRACE_SETREGS`, `COMPAT_PTRACE_GETFPREGS`, `COMPAT_PTRACE_SETFPREGS`, `COMPAT_PTRACE_GET_THREAD_AREA`, `COMPAT_PTRACE_SET_SYSCALL`, `COMPAT_PTRACE_GETVFPREGS`, `COMPAT_PTRACE_SETVFPREGS`, `COMPAT_PTRACE_GETHBPREGS`, `COMPAT_PTRACE_SETHBPREGS`
- Generator directives/preprocessor guards: `#sorted`, `#From arch/arm64/include/asm/ptrace.h`, `#Prefix COMPAT_PTRACE_`, `#if defined __arm64__ || defined __aarch64__`, `#endif`

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
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/xlat/compat_ptrace_cmds.in -->
