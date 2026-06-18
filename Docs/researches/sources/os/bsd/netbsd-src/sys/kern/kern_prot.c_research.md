# File Research: sources/os/bsd/netbsd-src/sys/kern/kern_prot.c

## Purpose

`kern_prot.c` implements process/protection-related system calls: PID/session/group queries, UID/GID queries, UID/GID mutations, supplemental groups, `setsid`, `setpgid`, `issetugid`, and login-name get/set.

## Main Responsibilities

- Simple identity syscalls:
  - `getpid`, `getppid`, combined PID/PPID return variants.
  - `getuid`, `geteuid`, combined UID/EUID return variant.
  - `getgid`, `getegid`, combined GID/EGID return variant.
- Process group/session syscalls:
  - `getpgrp`
  - `getsid`
  - `getpgid`
  - `setsid`
  - `setpgid`
- Credential mutation:
  - `do_setresuid()`
  - `do_setresgid()`
  - wrappers for `setuid`, `seteuid`, `setreuid`, `setgid`, `setegid`, `setregid`.
- Supplemental groups:
  - `getgroups`
  - `setgroups`
- Session login name:
  - `__getlogin`
  - `__setlogin`
- SUGID query:
  - `issetugid`

## Credential Mutation Model

- `do_setresuid()` and `do_setresgid()` are the core implementations.
- They allocate a new credential, enter process credential modification via `proc_crmod_enter()`, validate whether requested IDs match permitted current IDs, and otherwise ask kauth for `KAUTH_PROCESS_SETID`.
- UID changes update process and LWP accounting:
  - `chgproccnt()` for process count by real UID.
  - `chglwpcnt()` for LWP count by real UID, excluding the first LWP.
- If nothing changes, the functions leave without broadcasting a new credential.
- On change:
  - clone current credential;
  - set requested real/effective/saved IDs;
  - call `proc_crmod_leave(newcred, oldcred, true)` to publish and mark `PK_SUGID`.

## Process Group and Session Behavior

- `sys_setsid()` calls `proc_enterpgrp(p, p->p_pid, p->p_pid, true)` and returns the process PID.
- `sys_setpgid()` normalizes `pid == 0` to caller PID and `pgid == 0` to target PID, rejects negative pgid, then delegates to `proc_enterpgrp()`.
- `getpgrp`, `getsid`, and `getpgid` use `proc_lock` for process group/session state.

## Groups and Login Name

- `sys_getgroups()` returns group count if `gidsetsize == 0`; otherwise validates capacity and uses `kauth_cred_getgroups()`.
- `sys_setgroups()` builds a new credential group list with `kauth_cred_setgroups()` and commits via `kauth_proc_setgroups()`.
- `sys___getlogin()` copies the session login name under `proc_lock`.
- `sys___setlogin()` requires `KAUTH_PROCESS_SETID`, copies a bounded user string, warns if a non-session-leader changes an already-set login name, then stores it in the session.

## Security Notes

- Non-root ID changes are constrained by current real/effective/saved IDs and explicit flag masks.
- Privileged override is mediated through kauth.
- `issetugid` reports `PK_SUGID`, which NetBSD treats as tainted not only after setuid exec but also after ownership changes.
