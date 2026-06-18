# File Research: sources/os/bsd/netbsd-src/sys/sys/Makefile

Read completely: 81 lines.

Installs public kernel/userland headers from `sys/sys` into `/usr/include/sys`.

Key behavior:
- Sets `INCSDIR=/usr/include/sys`.
- `INCS` enumerates the exported system headers, including filesystem/VFS-relevant headers such as `acl.h`, `extattr.h`, `mount.h`, `uio.h`, `vnode.h`, `vnode_if.h`, `wapbl.h`, `wapbl_replay.h`, and `xattr.h`.
- `INCSYMLINKS` creates compatibility/convenience symlinks for selected headers such as `fcntl.h`, `poll.h`, hashing headers, std headers, `syslog.h`, and `termios.h`.
- Adds `../soundcard.h` as `${INCSDIR}/soundcard.h`.
- Provides generation rules for `namei` from `namei.src` via `gennameih.awk`, and `device_calls.h` from `../kern/device_calls` via `gendevcalls.awk`.
- Includes `<bsd.kinc.mk>` for kernel include installation mechanics.

Risks and notes:
- Header installation surface is explicit; missing a header from `INCS` prevents it from being installed for userland/kernel consumers.
- Generated headers depend on tool awk and source files in neighboring directories.
