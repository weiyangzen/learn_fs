# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libmp/Makefile

Builds drawterm’s multiprecision integer library `libmp.a`.

Key content:
- Notes that the library is used only for `secstore` and need not be fast.
- Archives conversion, arithmetic, division, modular arithmetic, CRT, formatting, random, vector, and string-conversion objects.
- Includes more objects than this group covers, such as `mptobe`, `mpvecadd`, `strtomp`, and integer conversion files.
