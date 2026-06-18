# File Research: sources/os/bsd/freebsd-src/sys/sys/asan.h

Kernel address sanitizer interface.

Key elements:
- Under `KASAN`, defines shadow scale constants and stack/redzone poison byte values.
- Declares KASAN initialization, shadow mapping, poisoning, and thread allocation functions.
- Without `KASAN`, defines no-op macros for the same operations.

Dependencies:
- Under `KASAN`, includes `sys/types.h` and uses `vm_offset_t`, `size_t`, `uint8_t`, and `struct thread`.

Research notes:
- Imported from NetBSD KASAN heritage.
- Useful for detecting memory bugs in kernel subsystems, including filesystem and storage code.
