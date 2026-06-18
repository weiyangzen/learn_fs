# File Research: sources/os/bsd/openbsd-src/sys/kern/kern_prot.c

Purpose: Implements process identity, credentials, process groups/sessions syscalls, group membership, login name, TCB syscalls, and thread names.

Key behavior:
- Simple getters return pid, thread id, parent pid, pgrp, session, uid/gid variants, groups, and `issetugid`.
- `sys_setsid()` and `sys_setpgid()` enforce POSIX session and process-group rules using `prfind()`, `pgfind()`, `inferior()`, and pgrp creation helpers.
- UID/GID mutation syscalls copy credentials before modification, enforce root/current-id permissions, mark `PS_SUGID`, and adjust per-UID process counts when real UID changes.
- `sys_setgroups()` requires root and replaces supplementary groups.
- `groupmember()`, `suser()`, and `suser_ucred()` provide group/root checks.

Credential lifecycle:
- `crget()`, `crhold()`, `crfree()`, `crcopy()`, and `crdup()` manage pooled reference-counted credentials.
- `crset()` copies the mutable credential region.
- `crfromxucred()` converts exported user credentials into kernel credentials.

Filesystem/security relevance:
- Credentials maintained here are used throughout VFS permission checks, signal authorization, coredump ownership, and pledge helpers.
- `proc_cansugid()` blocks privilege elevation for traced processes or processes sharing file descriptor tables.
- `dorefreshcreds()` updates a thread's cached credential pointer from its process credential.
