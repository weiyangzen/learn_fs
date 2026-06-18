<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/x86_64/rt_sigframe.h -->
# sources/test-tools/strace/src/linux/x86_64/rt_sigframe.h

Purpose: declares the x86_64 runtime signal-frame header used by signal-return decoders.
Important APIs/types/functions: `struct_rt_sigframe` with `pretcode` and `ucontext_t`; i386 include fallback under `__i386__`.
Control flow: preprocessor selects native or i386 definition. State and persistence behavior: type declaration only.
Dependencies and integration points: `arch_rt_sigframe.c` and signal frame printers. Risks: incomplete structure intentionally notes more data follows; consumers must not assume full frame coverage. Test signals: signal-delivery and rt_sigreturn decoding tests.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/x86_64/rt_sigframe.h -->
