<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/attic/test/x32_lseek.c -->
# sources/test-tools/strace/attic/test/x32_lseek.c

Purpose: x32 ABI probe to confirm `lseek` uses a full 64-bit offset and that strace prints it correctly.

Important logic: compile-time assertion requires `sizeof(long) > 4`. Opens `/etc/passwd` on fd 0, performs raw `syscall(__NR_lseek | 0x40000000, 0, 0x12345678901, SEEK_SET)`, prints return position and errno, then reports whether the offset was preserved.

Control flow: single raw syscall with x32 syscall bit set.

State and persistence: read-only file open and file offset update.

Dependencies and integration: x86_64 build environment with x32 syscall compatibility and `<asm/unistd.h>`.

Risks: host kernels may not support x32. Opening `/etc/passwd` assumes the path exists. The compile assertion name says 64 bits, but x32 has 32-bit long in normal ABI, so build instructions use x86_64 compiler to issue x32-numbered syscall. Test signals: strace output should show `lseek(0, 1250999896321, SEEK_SET)`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/attic/test/x32_lseek.c -->
