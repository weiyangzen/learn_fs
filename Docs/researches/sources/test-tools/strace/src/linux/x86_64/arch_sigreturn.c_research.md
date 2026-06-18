<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/x86_64/arch_sigreturn.c -->
# sources/test-tools/strace/src/linux/x86_64/arch_sigreturn.c

Purpose: wires x86_64 signal-return handling to the shared i386 implementation.
Important APIs/types/functions: includes `../i386/arch_sigreturn.c`.
Control flow: no local functions. State and persistence behavior: none locally.
Dependencies and integration points: integrates with syscall decoders for `sigreturn`/`rt_sigreturn` and architecture frame definitions. Risks: include-level coupling can mask x86_64-specific changes. Test signals: signal-return decoding tests under native, i386, and x32 personalities.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/x86_64/arch_sigreturn.c -->
