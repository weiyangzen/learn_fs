# File Research: sources/os/plan9/9front/sys/src/cmd/rc/pfnc.c

Debug printer for bytecode execution. Maps opcode function pointers to human-readable names and prints the current source location, pid, code vector, pc, opcode, and argv stack.

Enabled from the main interpreter when `flag['r']` is set. Useful for tracing compiled `rc` programs at opcode granularity.
