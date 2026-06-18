# File Research: sources/os/plan9/9front/sys/src/cmd/5i/arm.h

This header defines the global model for the `5i` ARM interpreter/debugger.

Key structures:
- `Breakpoint`: type, address, count/value, done counter, and next link.
- `Tlb`: simulated TLB status, size, entries, hits, and misses.
- `Icache`: simulated instruction cache settings, line array, hash function, and stats.
- `Inst`: decoded instruction table entry: function, name, type, count, taken, and delay use.
- `Registers`: current address/instruction, instruction pointer, 16 integer regs, condition/compare bookkeeping, class, carry fields.
- `Segment`: simulated memory segment metadata, lazy page table, ref counters, and file offsets.
- `Memory`: array of segments.

Constants:
- Breakpoint types: instruction/read/write/access/equal.
- Instruction classes: memory, arithmetic, branch, syscall.
- Registers: argument/return, PC, link, SP.
- Segment IDs: stack, text, data, BSS.
- Plan 9 constants: page size, word size, user text base, stack top/size, profiling granularity, S bit, sign bit, FP condition constants.

Declarations:
- Interpreter execution, command shell, breakpoints, memory access, fetch, stack/source printing, profiling summaries, TLB/cache, syscall, arithmetic helpers, and allocation functions.
- Globals for registers, memory, trace flags, instruction tables, cache/TLB, breakpoints, command state, symbol map, and profiling.

Dependencies and interactions:
- Included by all `5i` files.
- Uses Plan 9 `mach` symbol/disassembly interfaces.

Research relevance:
- Defines the state contract for the interpreter/debugger.

Risk notes:
- Some function names and FP constants reflect inherited MIPS interpreter code, while the target is ARM.
- Many globals are shared mutable state across command, memory, breakpoint, and execution layers.
