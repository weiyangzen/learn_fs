# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/posix-386/Makefile

Builds `../libmachdep.a` for POSIX i386 drawterm. Object files are `getcallerpc.$O`, `md5block.$O`, `sha1block.$O`, and `tas.$O`.

Rules:
- C files compile with `$(CC) $(CFLAGS)`.
- Assembly files assemble with `$(AS) -o`.
- `md5block.s` and `sha1block.s` are generated from `.spp` files via `gcc -E -`.

Notable role: this architecture uses hand-generated assembly hash blocks and x86 test-and-set.
