<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/x86_64/ioctls_arch1.h -->
# sources/test-tools/strace/src/linux/x86_64/ioctls_arch1.h

Purpose: compat i386 ioctl architecture table shim for x86_64 personality 1.
Important APIs/types/functions: includes `../i386/ioctls_arch0.h`.
Control flow: no local logic. State and persistence behavior: build-time alias.
Dependencies and integration points: ioctl decoder under i386 personality. Risks: wrong include would mislabel compat ioctl numbers. Test signals: 32-bit tracee ioctl decoding tests on x86_64 hosts.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/x86_64/ioctls_arch1.h -->
