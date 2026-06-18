# File Research: sources/os/plan9/plan9/sys/src/9/pc/main.c

- Size/hash: 982 lines, 19158 bytes, SHA-256 `632e80c024419ef6cbcf0b2c7764ae88b1b337095ec0b855e3ceb1573bb940ef`.
- Purpose: Main PC kernel bootstrap and machine-dependent process, FPU, reboot, configuration, and idle support.
- Global state: Defines `Mach *m`, `Conf conf`, boot/config arrays, `bootdisk`, initial user stack pointer `sp`, `delaylink`, and idle policy flags.
- Boot option parsing: `options` reads boot loader configuration from `BOOTARGS`, strips CR, normalizes tabs, splits `name=value` lines, ignores comments, and fills `confname/confval`.
- Main boot sequence: `main` performs early console/video setup, machine init, option parsing, I/O init, trap/MMU init, keyboard/timer/CPU/memory/config/arch setup, link loading, device reset, page/swap/user process init, then enters `schedinit`.
- Machine init: `mach0init` binds CPU0 `Mach`, PDB, and GDT addresses; `machinit` clears and reinitializes the current `Mach` with a temporary delay constant.
- First process: `userinit` creates `*init*`, allocates kernel/user stacks and text, calls `bootargs`, copies `initcode` into user text, and makes the process ready.
- User boot args: `bootargs` builds initial argv for `/386/9dos`, converts boot-line prefixes like `fd`, `sd`, and `ether`, and lays argc/argv onto the user stack.
- Configuration sizing: `confinit` computes process/image/swap counts, kernel/user page split, and pool sizes based on memory and `*kernelpercent`.
- FPU handling: `mathinit` installs handlers for coprocessor error, emulation fault, and segment overrun; helper routines save/restore x87/SSE state, post notes, and protect note handlers.
- Process machine state: `procsetup`, `procrestore`, and `procsave` manage lazy FPU state and process cycle accounting, flushing TLBs when saving.
- Shutdown/reboot: `shutdown` coordinates multi-CPU exit and panic delays; `reboot` writes config back, moves to CPU0, shuts down devices/interrupts, maps low memory, installs `rebootcode`, and jumps to the reboot trampoline; `exit` calls arch reset.
- Misc utilities: `isaconfig` parses ISA config entries; `cistrcmp` and `cistrncmp` provide case-insensitive matching; `idlehands` halts based on CPU count and idle policy.
- Dependencies: Touches nearly every PC and port subsystem: `ioinit`, `i8250console`, `trapinit`, `mmuinit`, `kbdinit`, `i8253init`, `cpuidentify`, `meminit`, `archinit`, `links`, `chandevreset`, `pageinit`, `swapinit`, scheduler, channels, pools, and reboot code.
- Research notes: This is the PC kernel orchestration point. Filesystem relevance is direct at boot: root channel initialization, device reset/link loading, swap init, and launch of `/boot`.
