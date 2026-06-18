# File Research: sources/os/plan9/9front/sys/src/9/bcm/arch.c

Shared ARM/BCM architecture glue for process state and user register handling.

Key behavior:
- Fills kernel `Ureg` context for sleeping process stack traces.
- Enforces word-aligned user addresses.
- Returns debug/user PC from `up->dbgreg`.
- Masks protected PSR bits when writing registers through proc interfaces.
- Sets kernel process scheduler stack/PC.
- Hooks FPU process setup/fork/save/restore.
- Switches away from user page tables on SMP during process save.
- Implements `userureg` and a spl-protected `cas32`.

Dependencies:
- Uses ARM PSR constants, FPU helpers, MMU switch, and process state.

Research notes:
- This is architectural glue rather than board-specific code.
