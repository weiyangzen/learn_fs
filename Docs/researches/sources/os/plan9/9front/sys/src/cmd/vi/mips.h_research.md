# File Research: sources/os/plan9/9front/sys/src/cmd/vi/mips.h

`mips.h` is the shared simulator header. It defines MIPS user/kernel address constants, breakpoint types, instruction classes, TLB and icache models, decoded instruction table entries, register file including FP unions, memory segments, syscall memory-copy modes, global state, function prototypes, Plan 9 page/stack constants, opcode field macros, and FP compare constants.

The header is the integration point for the debugger, memory model, instruction execution, syscall layer, stats, and process setup. It also imports `/mips/include/ureg.h`, binding this tool to Plan 9 MIPS register layout.
