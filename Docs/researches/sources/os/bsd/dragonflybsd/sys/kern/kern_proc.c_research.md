# File Research: sources/os/bsd/dragonflybsd/sys/kern/kern_proc.c

This file manages global process, process-group, session, and process-table sysctl infrastructure. It includes PID allocation/reuse delay, process holds, zombie serialization, pgrp/session reference lifetimes, job-control orphan handling, process/LWP shared user maps, process scans, and `kern.proc` sysctl handlers.

Global organization:
- Process, pgrp, and session lists are sharded across `ALLPROC_HSIZE` buckets, each with a `proc_token`.
- `pid_doms[]` records recent pid/pgid/sid reuse domains so `proc_makepid()` can avoid recycling identifiers too quickly.
- `randompid` optionally adds random offset to PID allocation and is controlled by `kern.randompid`.

Important functions:
- `procinit()` allocates and seeds `pid_doms[]`, initializes bucket lists/tokens, and initializes uidinfo hashing.
- `pfind()`, `pfindn()`, and `zpfind()` find live or zombie processes by PID, with `pfind()`/`zpfind()` returning held references.
- `phold()`, `prele()`, `pstall()`, `pholdzomb()`, `prelezomb()`, `pwaitres_set()`, and `pwaitres_pending()` implement process hold and zombie-reaping interlocks using `p_lock` bitfields.
- `pgfind()`, `pgref()`, `pgrel()`, `enterpgrp()`, and `leavepgrp()` manage process groups, including hash insertion/removal and references to sessions.
- `sess_hold()` and `sess_rele()` manage session lifetimes and terminal association cleanup.
- `fixjobc()` and `orphanpg()` maintain terminal job-control eligibility and send `SIGHUP`/`SIGCONT` when a stopped process group becomes orphaned.
- `proc_add_allproc()` and `proc_makepid()` allocate a PID, avoid active process/pgrp/session conflicts, obey reuse-domain delay, and insert into the allproc hash.
- `proc_move_allproc_zombie()` marks a process zombie; `proc_remove_zombie()` removes it from allproc and sibling lists and records its PID domain as recently used.
- `proc_usermap()`, `proc_userunmap()`, `lwp_usermap()`, and `lwp_userunmap()` manage shared user/kernel mapping metadata for process and thread titles, IDs, fork IDs, and runtime fields.
- `allproc_scan()`, `alllwp_scan()`, and `zombproc_scan()` provide callback-based scans with holds and optional per-CPU segmentation.

Sysctl surface:
- `sysctl_kern_proc()` implements `kern.proc` queries by PID, all, pgrp, tty, uid, and ruid, with optional LWP and LWKT-thread output flags. It checks `ps_showallprocs`, jail visibility, and credential trespass rules.
- It can also scan per-CPU LWKT thread queues by migrating the current thread to each CPU when LWKT output is requested.
- `sysctl_kern_proc_args()` gets or sets process/thread titles and argument strings, using `p_upmap` and `lwp_lpmap` overrides when present.
- `sysctl_kern_proc_cwd()` reports a process current directory via namecache fullpath.
- `sysctl_kern_proc_pathname()` reports executable path from `p_textnch`.
- `sysctl_kern_proc_sigtramp()` reports signal trampoline address range for the current process ABI.

Concurrency and permissions:
- Bucket `proc_token`s protect list traversal and insertion/removal.
- `PHOLD()` prevents process structures from disappearing during scans.
- Process and LWP tokens serialize detailed state access.
- Jail and credential checks gate user-visible process information.

Filesystem/storage relevance:
- Process cwd/pathname sysctls traverse namecache state. PID/session/pgrp and credentials underpin file ownership, signal, lock, and process visibility rules used by filesystem-facing tools.

Notable risk/quirk:
- In `sysctl_kern_proc_args()`, the process-title update path checks `sizeof(lp->lwp_lpmap->thread_title)` even when `lp` is NULL. This appears to be a likely typo for the process title buffer and would be unsafe if compiled/executed as shown.
