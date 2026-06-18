# File Research: sources/os/plan9/plan9/sys/src/9/teg2/softfpu.c

Fallback software-FPU integration file.

Key behavior:
- Most process/FPU lifecycle hooks are stubs.
- `fpuemu(Ureg*)` calls `fpiarm(ureg)` under an error handler, posts a debug note on failure, and returns whether FP instructions were emulated.
- `fpon`, `fpoff`, and `fpuinit` are empty.

Notes:
- This is the no-real-VFP or software-only counterpart to `vfp3.c`.
- Allows portable proc/syscall code to call machine FPU hooks even when they do nothing.
