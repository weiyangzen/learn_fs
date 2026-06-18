# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/iostack.h

Operand-stack pointer API header.

Key contents:
- Includes `iosdata.h` and `istack.h`.
- Defines `os_ptr` as `s_ptr`.
- Defines `const_os_ptr` as `const_s_ptr`.

Notable dependencies:
- `iosdata.h`.
- `istack.h`.

Research notes:
- This header gives operand-stack-specific names to generic ref-stack pointer types.
- It is intentionally minimal; actual stack behavior comes from the shared stack implementation.
