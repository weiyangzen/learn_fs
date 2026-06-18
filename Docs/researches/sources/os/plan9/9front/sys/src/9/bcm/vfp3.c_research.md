# File Research: sources/os/plan9/9front/sys/src/9/bcm/vfp3.c

ARM VFPv3 floating-point detection, context management, and emulation glue.

Key responsibilities:
- Detects supported floating-point implementation/subarchitecture.
- Enables/disables VFP access and configures FPSCR/FPEXC.
- Allocates, saves, restores, forks, and releases per-process FP state.
- Saves FP state for note delivery and restores after notes.
- Handles floating-point unavailable/math traps and posts math notes.
- Provides limited emulation/condition handling for trapped FP instructions.

Important behavior:
- Uses lazy process FP ownership to avoid unnecessary save/restore.
- Kernel and user FP state transitions are carefully separated.
- `fpstuck()` detects repeated FP faults at the same PC.

Dependencies:
- ARM VFP system-register assembly helpers, `FPsave`, process note machinery, trap handling, and scheduler process hooks.
