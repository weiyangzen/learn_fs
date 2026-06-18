# File Research: sources/os/bsd/dragonflybsd/sys/kern/kern_prot.c

This file implements process identity, process-group/session, UID/GID, group-list, credential, login-name, and protection-related syscalls/helpers.

Identity and group/session syscalls:
- `sys_getpid()`, `sys_getppid()`, `sys_lwp_gettid()`, `sys_getpgrp()`, `sys_getpgid()`, and `sys_getsid()` return process, parent, LWP, pgrp, and session identifiers.
- `sys_setsid()` creates a new session by calling `enterpgrp()` when the process is not already a pgrp/session leader.
- `sys_setpgid()` validates POSIX setpgid rules: target must be self or child, same session, not execed, not session leader, and target pgrp must exist in the same session unless creating a new pgrp.

UID/GID and groups:
- `sys_getuid()`, `sys_geteuid()`, `sys_getgid()`, `sys_getegid()`, `sys_getgroups()`, `sys_getresuid()`, and `sys_getresgid()` expose credential fields.
- `sys_setuid()`, `sys_seteuid()`, `sys_setgid()`, `sys_setegid()`, `sys_setreuid()`, `sys_setregid()`, `sys_setresuid()`, and `sys_setresgid()` implement traditional BSD/POSIX saved-ID semantics with capability checks.
- `sys_setgroups()` requires `SYSCAP_NOCRED_SETGROUPS`, copies user group IDs, and marks the process SUGID.
- `groupmember()` tests group membership.

Thread names and process taint:
- `sys_lwp_setname()` and `sys_lwp_getname()` store/retrieve per-LWP titles through `lwp_lpmap`.
- `sys_issetugid()` reports whether `P_SUGID` is set.
- `setsugid()` marks the process as tainted and clears stop state unless protected by procfs flags.

Credential management:
- `crget()`, `crhold()`, and `crfree()` allocate, reference, and release credentials, including uidinfo and prison references.
- `cratom()` and `cratom_proc()` copy credentials before mutation when shared; `cratom_proc()` replaces `p_ucred` under `p_spin` to handle multi-thread syscall-entry races.
- `crdup()` duplicates a credential; `crdup_nocaps()` duplicates without caps or prison state.
- `cru2x()` exports a `struct xucred`.
- `change_euid()` and `change_ruid()` update effective/real UID and associated uidinfo/process/file-lock accounting.

Protection checks:
- `p_trespass()` determines whether one credential can act on another. It enforces prison boundaries, restricted-root constraints, matching real/effective UID combinations, `SYSCAP_NOPROC_TRESPASS`, and root fallback.
- `sys_getlogin()` and `sys_setlogin()` read/write session login name, with `SYSCAP_NOPROC_SETLOGIN` required for writes.

Concurrency:
- Mutating syscall paths generally hold `p_token`.
- Credential replacement uses copy-on-write plus `p_spin`.
- Copyout-heavy getters avoid holding shared tokens where synchronous faults could be problematic.

Filesystem/storage relevance:
- Credentials, group membership, SUGID state, and trespass checks feed file permission decisions, ownership changes, locking behavior, and process visibility for filesystem tools.

Notable risk/quirk:
- Disabled `_POSIX_SAVED_IDS` branches contain apparent typos (`crc`, `cpas_priv_check`) but are inside conditional code not active in the visible default path.
