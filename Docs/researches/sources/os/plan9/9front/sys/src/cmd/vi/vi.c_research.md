# File Research: sources/os/plan9/9front/sys/src/cmd/vi/vi.c

`vi.c` is the main program and setup code for the MIPS simulator/debugger. It opens a MIPS executable or attaches to an existing process id, initializes Bio streams, TLB defaults, executable headers, symbols, memory maps, stack, initial FP constants, then enters `cmd()`.

`initmap()` builds text, data, bss, and stack segments from executable header layout and allocates instruction profiling storage. `procinit()` snapshots `/proc/<pid>` text, segment, memory, registers, and stack into simulator state. `initstk()` constructs a Plan 9-style user stack with argc/argv and a minimal `Tos`.

The file also provides fatal/error reporting, instruction trace formatting, register dumps, allocation helpers, and signed/unsigned 32x32-to-64 multiplication helpers used by simulated multiply instructions.
