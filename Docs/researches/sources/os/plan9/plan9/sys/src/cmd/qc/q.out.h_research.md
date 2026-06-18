# File Research: sources/os/plan9/plan9/sys/src/cmd/qc/q.out.h

PowerPC object/instruction ABI header shared by the compiler backend and associated tools.

Key contents:
- Defines register numbers and register allocation ranges for integer and floating-point registers.
- Enumerates all backend assembler opcodes, including integer, branch, floating-point, cache/control, embedded PowerPC, optional 32-bit FP, and paired/secondary FP instructions.
- Defines address type/name classes such as extern/static/auto/param, branches, registers, constants, FPSCR/MSR/SPR/SREG, files, and DCRs.
- Defines object flags `NOPROF` and `DUPOK`.
- Defines the archive symbol name `__.SYMDEF`.
- Provides the simulated IEEE double layout used by object emission.

Dependencies:
- Used by `qc`, `ql`, assemblers, and tools that read/write PowerPC Plan 9 object streams.

Notable risks:
- This is an ABI-style enum header. Opcode or address-class order changes would break object compatibility with the linker and disassembler.
- Register allocation comments encode target calling/register conventions expected by `txt.c` and `reg.c`.
