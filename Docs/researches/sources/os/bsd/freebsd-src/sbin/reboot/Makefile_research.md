# File Research: sources/os/bsd/freebsd-src/sbin/reboot/Makefile

Build file for reboot-family commands.

Key elements:
- Builds `reboot` in package `runtime`.
- Installs manpages `reboot.8` and `nextboot.8`, plus architecture boot manpages when present.
- Creates hard links/symlinks from `reboot` to `halt`, `fastboot`, `fasthalt`, and `nextboot`.

Dependencies:
- Uses machine-specific manpage conditionals and `bsd.prog.mk`.
