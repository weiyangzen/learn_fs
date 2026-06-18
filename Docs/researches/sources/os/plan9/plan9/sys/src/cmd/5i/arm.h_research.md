# File Research: sources/os/plan9/plan9/sys/src/cmd/5i/arm.h

## Scope

Shared declarations, constants, structs, and globals for the `5i` emulator/debugger.

## Contents

- Defines breakpoint types, instruction classes, register numbers, TLB/cache structures, instruction dispatch entries, CPU register state, memory segments, and memory-copy modes.
- Declares emulator APIs for memory, execution, breakpoints, symbols, commands, syscall dispatch, profiling, and initialization.
- Declares global emulator state: `reg`, `memory`, `text`, `trace`, `sysdbg`, `calltree`, `itab`, `icache`, `tlb`, breakpoints, I/O buffers, profile data, and symbol map.
- Defines Plan 9 ARM constants such as page size, stack top, stack size, condition-code modes, and FP condition bits.

## Dependencies

Includes are supplied by each C file; this header depends conceptually on Plan 9 `Map`, `Biobuf`, `jmp_buf`, and Mach symbol types.

## Risks And Invariants

- Globals are declared through the `EXTERN` macro; exactly one compilation unit (`syscall.c`) defines them.
- Several declared functions are stubs or legacy names, reflecting partial emulator coverage.
