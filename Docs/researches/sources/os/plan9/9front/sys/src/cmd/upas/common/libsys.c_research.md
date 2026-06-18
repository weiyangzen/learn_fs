# File Research: sources/os/plan9/9front/sys/src/cmd/upas/common/libsys.c

This is the main Plan 9 system abstraction layer for upas mail commands.

Key behavior:
- Date/user/system/domain helpers: `thedate`, `getlog`, `sysname_read`, `alt_sysname_read`, `sysnames_read`, `domainname_read`.
- Lock helpers: per-directory `L.mbox` naming, `syslock`, `trylock`, `syslockrefresh`, `sysunlock`.
- File helpers: `sysopen`, `sysclose`, `sysmkdir`, `sysrename`, `sysexist`, create/open/unlock locked wrappers.
- Process/session helpers: `syskill`, `syskillpg`, `sysdetach`, pipe-write note handling through `pipesig`.
- Terminal helpers: console detection, hold-on/hold-off, `sysopentty`.
- Mailbox path and identity helpers: `mboxpathbuf`, `username`, `createfolder`, `creatembox`.

Integration and risks:
- Heavily shared by common mail tools and filterkit.
- Lock creation is intentionally tolerant: some lock errors are logged and then mail proceeds without a lock.
- `sysopen` mode string parsing is compact but non-obvious; callers depend on Plan 9 permission bits such as `DMAPPEND` and `DMEXCL`.
