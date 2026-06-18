# File Research: sources/os/plan9/plan9/sys/src/9/boot/local.c

Local disk boot method support for KFS and Fossil/Venti roots.

Key behavior:
- `configlocal()` selects boot disk from explicit root prompt, MIPS-style argv, method arg, `bootdisk` environment, or compiled default, and exports it.
- `connectlocalkfs()` detects a KFS partition/file, forks `/boot/kfs -f <partition> -s`, waits for startup, and returns pipe fd.
- `connectlocalfossil()` detects Fossil config, optionally starts local or network Venti, starts `/boot/fossil`, opens posted `#s/fboot`, and returns it.
- `configloopback()` creates loopback IP interface for local Venti.
- `connectlocal()` binds device namespaces, mounts USB parts, then tries Fossil before KFS.
- `run()`/`runv()` are synchronous fork/exec helpers.

This is the primary local-storage root filesystem boot path.
