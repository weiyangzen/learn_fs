<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/xtensa/ioctls_arch0.h -->
# sources/test-tools/strace/src/linux/xtensa/ioctls_arch0.h

Purpose: Xtensa architecture-specific ioctl request table.
Important APIs/types/functions: declarative ioctl rows mapping encoded request numbers to names/header origins.
Control flow: no executable code; searched by the generic ioctl decoder. State and persistence behavior: static table data.
Dependencies and integration points: ioctl symbolic decoding for Xtensa personality 0. Risks: stale constants lead to numeric or wrong ioctl output. Test signals: ioctl table generation checks and Xtensa ioctl smoke tests.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/xtensa/ioctls_arch0.h -->
