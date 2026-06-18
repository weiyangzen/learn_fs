# File Research: sources/os/plan9/9front/sys/src/cmd/cc/compat.h

Purpose: Declares OS compatibility helpers shared by compilers, linkers, and assemblers.

Key points:
- Defines system type bits: `Plan9`, `Unix`, and `Windows`.
- Declares wrappers for system-type detection, path separator, file access/creation, working directory, exec, dup, fork, pipe, and wait.
- Declares allocator helpers `alloc` and `allocn`.
- Uses `EXTERN` unless already defined.

Dependencies and interactions:
- Included by `cc.h`.
- Implementations are expected from the included compatibility source used by `compat.c`.

Research notes:
- Provides a portability abstraction for the Plan 9 compiler toolchain code.
