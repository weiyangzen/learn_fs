# File Research: sources/os/plan9/plan9/sys/src/9/teg2/vfp3.c

VFPv2/VFPv3 floating-point unit detection, configuration, lazy activation, save/restore, and trap integration.

Key behavior:
- Detects FP coprocessor access and VFP subarchitecture via CP15/FPSID.
- Configures FPSCR with default NaN, flush-to-zero, rounding, and exception masks.
- Lazily enables VFP on first user FP instruction and restores saved registers only when needed.
- Saves FP state for scheduling, `rfork`, and note delivery.
- Prevents FP use inside note handlers.
- Handles pending FP exceptions by posting Plan 9 debug notes.
- Falls back to `fpiarm` for old FPA opcodes.

Important functions:
- `havefp`, `fpinit`, `fpon`, `fpoff`, `fpsave`, `fprestore`.
- `fpuprocsave`, `fpusysprocsetup`, `fpunotify`, `fpunoted`.
- `fpuemu(Ureg*)`: trap-facing FP instruction handler.

Notes:
- Tracks stuck FP traps per CPU/process/PC to catch retry loops.
- Supports 16 or 32 VFP registers depending on hardware access bits.
