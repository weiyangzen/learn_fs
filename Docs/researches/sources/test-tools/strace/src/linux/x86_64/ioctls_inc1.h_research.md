<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/x86_64/ioctls_inc1.h -->
# sources/test-tools/strace/src/linux/x86_64/ioctls_inc1.h

Purpose: i386 compat ioctl include-set shim.
Important APIs/types/functions: includes `../i386/ioctls_inc0.h`.
Control flow: none. State and persistence behavior: compile-time include only.
Dependencies and integration points: x86_64 personality 1 ioctl table generation. Risks: missing compat headers reduce symbolic decoding. Test signals: i386 compat ioctl table and trace fixtures.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/x86_64/ioctls_inc1.h -->
