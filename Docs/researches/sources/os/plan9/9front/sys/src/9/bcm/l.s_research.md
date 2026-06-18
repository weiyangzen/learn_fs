# File Research: sources/os/plan9/9front/sys/src/9/bcm/l.s

Minimal 32-bit BCM bootstrap entry.

Key responsibilities:
- Provides `_start`.
- Sets the initial stack near `KTZERO`.
- Branches into `main`.

Role:
- Tiny architecture entry shim used with the rest of the BCM ARM assembly startup and exception code.

Dependencies:
- Memory layout constants from `mem.h` and the C `main()` entry.
