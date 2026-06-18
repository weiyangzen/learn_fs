# File Research: sources/os/bsd/netbsd-src/lib/libm/arch/i387/abi.h

x87/SSE ABI bridge macros for i387 assembly libm files. On x86-64 it spills XMM float/double arguments to stack slots so x87 instructions can consume them, then reloads return values back to XMM registers.

On i386 the prologue/epilogue macros are mostly empty because arguments are already stack-passed.
