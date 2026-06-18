<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/x86_64/ioctls_inc2.h -->
# sources/test-tools/strace/src/linux/x86_64/ioctls_inc2.h

Purpose: x32 ioctl include-set shim.
Important APIs/types/functions: includes `../x32/ioctls_inc0.h`.
Control flow: no executable logic. State and persistence behavior: compile-time include only.
Dependencies and integration points: x32 ioctl table generation. Risks: x32 ioctl structure-size differences are concentrated here and in generated tables. Test signals: x32 ioctl generation and pointer-size-sensitive ioctl tests.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/x86_64/ioctls_inc2.h -->
