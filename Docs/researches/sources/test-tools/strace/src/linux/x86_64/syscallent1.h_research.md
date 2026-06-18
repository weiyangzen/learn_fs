<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/x86_64/syscallent1.h -->
# sources/test-tools/strace/src/linux/x86_64/syscallent1.h

Purpose: x86_64 personality 1 syscall table shim for i386 tracees.
Important APIs/types/functions: includes `../i386/syscallent.h`.
Control flow: no local logic; table dispatch is delegated to i386 entries. State and persistence behavior: static include alias.
Dependencies and integration points: selected after register-size/personality detection. Risks: personality ordering mistakes map 32-bit processes to the wrong syscall table. Test signals: 32-bit tracee syscall-decoding coverage on x86_64 builds.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/x86_64/syscallent1.h -->
