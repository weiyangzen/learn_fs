# File Research: sources/os/plan9/9front/sys/src/cmd/qi/power.h

Shared header for the `qi` Power simulator/debugger.

Key contents:
- Includes `/power/include/ureg.h` and defines user/ureg address helpers.
- Defines `Registers`, `Segment`, `Memory`, `Inset`, `Inst`, `Icache`, and `Breakpoint`.
- Enumerates breakpoint types, instruction classes, memory copy directions, and segment types.
- Declares all major simulator functions and global state.
- Defines Plan 9 Power layout constants: page size, user text base, stack top/size, profiling granularity, NOP encoding, sign bit.
- Defines condition-register, FPSCR, XER, and instruction decode macros.

Dependencies and coupling:
- Included by all `qi/*.c` files.
- Depends on Plan 9 `mach` library types (`Map`, `Symbol`) and Power kernel ureg layout.

Filesystem/OS relevance:
- Encodes the simulated process memory model and syscall/debugger shared state.
