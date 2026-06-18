# File Research: sources/os/plan9/9front/sys/src/9/bcm/lexception.s

32-bit ARM exception vector and trap-entry assembly for BCM.

Key responsibilities:
- Defines the vector table and branch table.
- Handles SVC/syscall, undefined instruction, prefetch abort, data abort, IRQ, and FIQ entries.
- Saves user/kernel register state into Plan 9 `Ureg` layout.
- Switches to the kernel `Mach`/`Proc` context before calling C `syscall()`, `trap()`, `irq()`, and `fiq()`.
- Restores user state for `noteret`, `forkret`, and normal trap return.
- Provides `setr13()` to set per-mode stack pointers.

Important behavior:
- Adjusts link-register offsets for abort types before building the saved PC.
- Distinguishes user exceptions from kernel exceptions.
- Uses FIQ stack handling and direct FIQ dispatch.

Dependencies:
- ARM CPSR modes, `mem.h` register conventions, C trap/syscall/interrupt handlers, and Plan 9 `Ureg` layout.
