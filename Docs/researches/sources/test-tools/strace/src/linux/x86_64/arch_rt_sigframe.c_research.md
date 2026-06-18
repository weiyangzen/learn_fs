<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/x86_64/arch_rt_sigframe.c -->
# sources/test-tools/strace/src/linux/x86_64/arch_rt_sigframe.c

Purpose: reuses the i386 runtime signal-frame decoder for x86_64 where appropriate.
Important APIs/types/functions: includes `../i386/arch_rt_sigframe.c`.
Control flow: no local logic; all behavior is delegated to the shared implementation. State and persistence behavior: none locally.
Dependencies and integration points: signal-frame decoding in `rt_sigreturn` handling. Risks: delegated decoder must handle x86_64-specific frame shape through included headers. Test signals: rt_sigreturn/signal frame tests for native and compat processes.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/x86_64/arch_rt_sigframe.c -->
