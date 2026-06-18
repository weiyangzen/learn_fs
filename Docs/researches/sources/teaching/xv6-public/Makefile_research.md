# File Research: sources/teaching/xv6-public/Makefile

Builds the public x86 xv6 teaching kernel, boot images, user programs, filesystem image, documentation PDF, and emulator targets.

Key behavior:
- Defines kernel object list, toolchain/QEMU auto-detection, 32-bit freestanding C flags, linker flags, and PIE-disabling probes for newer GCC.
- Builds `bootblock` from `bootasm.S`/`bootmain.c`, signs it with `sign.pl`, and writes it plus `kernel` into `xv6.img`.
- Builds `kernelmemfs` by swapping `ide.o` for `memide.o` and embedding `fs.img`.
- Generates `vectors.S`, user syscall stubs, user programs prefixed with `_`, and `fs.img` via `mkfs`.
- Provides `qemu`, `qemu-nox`, `qemu-gdb`, Bochs, `clean`, distribution, print/PDF, and tarball rules.

Important interactions:
- `UPROGS` controls initial filesystem contents.
- `MEMFSOBJS` changes storage semantics from IDE-backed to memory-backed.
- `runoff`, `runoff1`, and `pr.pl` are documentation/paper-generation support.
