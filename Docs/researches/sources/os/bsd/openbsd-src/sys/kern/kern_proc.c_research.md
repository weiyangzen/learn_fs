# File Research: sources/os/bsd/openbsd-src/sys/kern/kern_proc.c

Purpose: Maintains process, thread, uid, process-group, session, and debugger-visible process bookkeeping.

Key behavior:
- `procinit()` initializes global process lists, pid/tid/pgrp/uid hash tables, and pools for `proc`, `process`, `rusage`, `ucred`, `pgrp`, and `session`.
- `uid_find()`, `uid_release()`, and `chgproccnt()` track per-UID process counts behind `uidinfolk`.
- Lookup helpers include `tfind()`, `tfind_user()`, `prfind()`, `pgfind()`, and `zombiefind()`.
- `inferior()` checks parent ancestry for operations such as `setpgid`.

Process groups and sessions:
- `enternewpgrp()` creates a new process group and optionally a new session, including controlling-terminal/session metadata.
- `enterthispgrp()` moves a process between groups and updates job-control counts.
- `leavepgrp()` and `pgdelete()` remove group membership and release sessions.
- `fixjobc()`, `killjobc()`, and `orphanpg()` implement terminal job-control rules, including SIGHUP/SIGCONT delivery to orphaned stopped groups.

Filesystem relevance:
- Session cleanup can revoke a controlling terminal vnode through `VOP_REVOKE()` and release `s_ttyvp`.
- Process/session state here is used by tty, signal, and VFS permission-adjacent code elsewhere.

Diagnostics:
- DDB helpers print process state, kill/stop processes, and dump process lists in several views.
