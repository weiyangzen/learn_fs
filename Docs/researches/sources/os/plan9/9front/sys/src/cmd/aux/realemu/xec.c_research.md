# File Research: sources/os/plan9/9front/sys/src/cmd/aux/realemu/xec.c

`xec.c` implements instruction execution for the real-mode x86 emulator. It covers stack control flow, interrupts, returns, enter/leave, push/pop families, flag transfer, arithmetic/logical/shift/rotate/bit operations, multiply/divide, condition evaluation, branches, loops, moves, sign/zero extension, string ops, I/O, CPUID, NOP, and HLT.

Execution uses `decode` to fill an `Inst`, advances RIP to the post-instruction offset, then dispatches through `exctab`. Traps restore RIP to `oldip` and longjmp out. `intr` pushes FLAGS/CS/IP and loads an interrupt vector from physical address `v*4`.

String instructions honor REP/REPNE/REPE and direction flag. Arithmetic helpers centralize flag setting for carry, overflow, sign, zero, and parity. Unsupported opcodes trap as `EBADOP`.

Notable simplifications: no floating point/MMX/control-register instruction support; CPUID returns a small synthetic Intel-like table; many flags are approximate enough for BIOS-style code but not a full CPU verification model.
