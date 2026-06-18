# File Research: sources/teaching/os161/kern/include/types.h

Master kernel type header. Its comment documents include-order conventions: every source includes `types.h` first, other headers should include direct dependencies, and lower-level headers precede higher-level subsystems.

It includes user-visible `kern/types.h` and machine-private `machine/types.h`, defines typed `userptr_t` and `const_userptr_t` as pointers to an opaque one-byte struct, then maps underscore ABI types to conventional kernel names such as `uint32_t`, `size_t`, `off_t`, `pid_t`, and socket-related types.

It also defines `CHAR_BIT`, `NULL`, `bool`, `true`, and `false`. The `userptr_t` design helps prevent accidental mixing of user and kernel pointers at compile time.
