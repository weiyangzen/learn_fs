<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/x32/syscallent1.h -->
# sources/test-tools/strace/src/linux/x32/syscallent1.h

Purpose: personality table shim that reuses the i386 syscall table for the secondary x32/i386 personality lane.
Important APIs/types/functions: single include of `../i386/syscallent.h`.
Control flow: no local logic; compilation aliases the i386 table into this personality slot. State and persistence behavior: static build-time include only.
Dependencies and integration points: depends on x86 personality dispatch and i386 syscall table maintenance. Risks: if the personality ordering changes, this include could bind the wrong ABI table. Test signals: mixed x86_64/x32/i386 trace tests should verify i386 numbers decode through personality 1.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/x32/syscallent1.h -->
