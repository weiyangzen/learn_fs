# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/posix-mips/Makefile

Builds `../libmachdep.a` for POSIX MIPS drawterm from `getcallerpc`, portable C MD5/SHA1 blocks, and assembly `tas.s`.

Rules:
- C via `$(CC) $(CFLAGS)`.
- Assembly via `$(AS) $(ASFLAGS) -o`.
- `.spp` files can be preprocessed with `cpp`.
