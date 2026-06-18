# File Research: sources/os/plan9/9front/sys/src/9/boot/bootfs.proto

Prototype file describing the base compressed boot filesystem.

Key contents:
- Includes architecture-specific binaries such as shell utilities, networking tools, authentication helpers, `cfs`, `mntgen`, and `tlsclient`.
- Installs rc support files, including `rcmain`, `reboot.rc`, `net.rc`, and `bootrc`.
- Creates basic directories: `tmp`, `sys/lib/kbmap`, and `lib/firmware`.

Role:
- Input manifest for building `/boot/bootfs.paq`.
