# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/iostack.h

Operand-stack pointer type header.

Key behavior:
- Includes `iosdata.h` and `istack.h`.
- Defines `os_ptr` as `s_ptr`.
- Defines `const_os_ptr` as `const_s_ptr`.

Research notes:
- This is a thin specialization layer so operand-stack code can use semantic pointer names while sharing generic stack machinery.
