# File Research: sources/os/plan9/9front/sys/src/9/arm64/fpu.c

ARM64 floating-point/SIMD lazy context management.

Key behavior:
- Saves and restores FP control/status and 32 vector registers through assembly helpers.
- Keeps separate user FP and nested kernel FP save stacks.
- Disables FP access by default and enables/restores state lazily on FP traps.
- Handles kernel FP use during syscalls, traps, and interrupts with `fpukenter`/`fpukexit`.
- Handles fork, save, restore, notify, and noted paths.
- Posts a floating-point error note for repeated user FP traps while already active.

Dependencies:
- Uses `getfcr/setfcr/getfsr/setfsr`, `fpon/fpoff`, `fpsaveregs/fploadregs`, process state, and note machinery.

Research notes:
- Kernel FP state can nest through linked `FPalloc` records.
- User state is protected during kernel entry so kernel vector use does not corrupt user registers.
