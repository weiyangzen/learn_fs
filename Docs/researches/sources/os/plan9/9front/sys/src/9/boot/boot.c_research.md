# File Research: sources/os/plan9/9front/sys/src/9/boot/boot.c

Small boot program that expands embedded boot filesystem and executes `bootrc`.

Key responsibilities:
- Binds `/boot` after `/bin`.
- Forks `paqfs` to mount `/boot/bootfs.paq` at `/root`.
- Binds `/root` onto `/`.
- Adds architecture-specific `/root/$cputype/bin` and `/rc/bin` into `/bin`.
- Replaces `/rc` with `/root/rc`.
- Executes `/bin/bootrc`.

Important behavior:
- Reads `/env/cputype` to choose the architecture bin directory.
- On failure, exits with the current error string.

Dependencies:
- User-level Plan 9 namespace calls, `paqfs`, embedded boot filesystem, and `bootrc`.
