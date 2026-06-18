# File Research: sources/os/bsd/freebsd-src/sbin/hastd/subr.c

`subr.c` contains HAST support routines: append-style `snprintf` wrappers, local provider probing, role string conversion, and privilege dropping.

`provinfo()` opens the configured local path if needed and accepts only character devices and regular files. Character devices are treated as GEOM providers queried with `DIOCGMEDIASIZE` and `DIOCGSECTORSIZE`; regular files use file size and a hardcoded 512-byte sector size.

`drop_privs()` resolves the `hast` user, jails or chroots into that user's home directory, switches to `/`, clears supplementary groups, sets gid/uid, optionally enters Capsicum, and limits capabilities/ioctls for local provider and primary ggate descriptors. It verifies real/effective/saved uid/gid and no supplementary groups before reporting success.
