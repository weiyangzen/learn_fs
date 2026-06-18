<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/x86_64/ioctls_arch0.h -->
# sources/test-tools/strace/src/linux/x86_64/ioctls_arch0.h

Purpose: native x86_64 architecture-specific ioctl number table.
Important APIs/types/functions: declarative rows mapping encoded ioctl request numbers to symbolic names and header origins.
Control flow: no executable flow; ioctl decoder searches generated tables to print known request names. State and persistence behavior: static read-only table.
Dependencies and integration points: consumed by generic ioctl lookup for personality 0. Risks: stale ioctl constants lead to numeric output or wrong names. Test signals: ioctl table generation checks and smoke tests for tty, block, input, and filesystem ioctls.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/x86_64/ioctls_arch0.h -->
