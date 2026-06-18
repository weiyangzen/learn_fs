# File Research: sources/os/bsd/dragonflybsd/sys/sys/jail.h

Defines DragonFly BSD jail user/kernel ABI and kernel prison structures. Userland gets `struct jail`, legacy `struct jail_v0`, and `jail()` / `jail_attach()` declarations. Kernel sections define `struct prison`, per-jail IP storage, jail capability bit numbers, and helpers for IP validation, local/nonlocal address selection, wildcard replacement, privilege checks, refcounting, and sysctl lifecycle.

Filesystem relevance: jail capabilities include VFS permissions such as `PRISON_CAP_VFS_CHFLAGS` and mount permissions for nullfs, devfs, tmpfs, procfs, and fusefs. `struct prison` also stores the jailed root `nchandle`, tying jail isolation directly to namecache/VFS root lookup.
