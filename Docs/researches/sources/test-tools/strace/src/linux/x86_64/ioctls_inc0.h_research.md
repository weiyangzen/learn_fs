<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/x86_64/ioctls_inc0.h -->
# sources/test-tools/strace/src/linux/x86_64/ioctls_inc0.h

Purpose: native x86_64 generated ioctl include-set shim.
Important APIs/types/functions: includes `../64/ioctls_inc.h`.
Control flow: none. State and persistence behavior: compile-time include only.
Dependencies and integration points: ioctl table generator and decoder. Risks: include-set mismatch omits architecture-visible ioctl constants. Test signals: generated ioctl-table rebuild and native ioctl symbol coverage checks.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/x86_64/ioctls_inc0.h -->
