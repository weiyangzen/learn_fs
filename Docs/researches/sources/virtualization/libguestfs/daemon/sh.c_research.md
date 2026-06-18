# File Research: sources/virtualization/libguestfs/daemon/sh.c

Runs arbitrary commands inside the guest root.

Important behavior:
- Before command execution, bind-mounts `/dev`, `/dev/pts`, `/proc`, `/sys`, and SELinux paths into the sysroot where possible.
- If networking is enabled, bind-mounts appliance `/etc/resolv.conf` read-only over guest `/etc/resolv.conf`, creating/removing a placeholder if needed.
- `do_command` requires a mounted root and non-empty argv, then runs command with `COMMAND_FLAG_DO_CHROOT`.
- Cleanup attributes unmount bind mounts and resolver mount.
- `do_command_lines` splits stdout into lines.
- `do_command_out` streams stdout over FileOut.
- `do_sh`, `do_sh_lines`, and `do_sh_out` execute `/bin/sh -c`.

Filesystem relevance: general-purpose chroot command execution against mounted guest filesystems, with temporary system pseudo-filesystem setup.
