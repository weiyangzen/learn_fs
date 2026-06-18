# File Research: sources/os/plan9/plan9/sys/src/cmd/qi/bpt.c

Breakpoint management for the PowerPC interpreter/debugger `qi`.

Key responsibilities:
- Lists instruction, read, write, access, and equality breakpoints with symbolized addresses.
- Parses breakpoint modifiers from debugger commands.
- Creates and deletes breakpoints.
- Checks breakpoints during instruction fetch and memory access/write paths.
- Supports pass counts through `count/done`, and equality breakpoints comparing memory contents against the configured value.

Dependencies:
- Uses `power.h` globals: `bplist`, `membpt`, `cmdcount`, `count`, `atbpt`, `bioout`.
- Depends on expression parsing in `cmd.c`, memory accessors in `mem.c`, and symbol formatting from libmach.

Notable risks:
- `delbpt()` increments `membpt` when deleting non-instruction breakpoints; that appears counterintuitive and can leave memory breakpoint checks enabled.
- Equality breakpoints read memory during breakpoint checking and can trigger memory faults.
