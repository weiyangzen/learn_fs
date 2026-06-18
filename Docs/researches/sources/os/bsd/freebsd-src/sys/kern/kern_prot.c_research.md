# File Research: sources/os/bsd/freebsd-src/sys/kern/kern_prot.c

## Purpose
Implements process identity, credential, group, visibility, signaling, debugging, and login/session protection syscalls and kernel helpers. This is the core credential/security policy file for UID/GID changes, process visibility checks, signal permission checks, debug permission checks, and `struct ucred` lifecycle.

## Major Responsibilities
- Implements identity getters: `getpid`, `getppid`, `getpgrp`, `getpgid`, `getsid`, `getuid`, `geteuid`, `getgid`, `getegid`, `getgroups`, `getresuid`, and `getresgid`.
- Implements session/process-group setters: `setsid()` and `setpgid()`.
- Implements credential mutation syscalls: `setcred`, `setuid`, `seteuid`, `setgid`, `setegid`, `setgroups`, `setreuid`, `setregid`, `setresuid`, and `setresgid`.
- Implements `issetugid()` and regression-only `__setugid`.
- Implements BSD visibility policies behind `security.bsd.see_other_uids`, `see_other_gids`, and `see_jail_proc`.
- Implements permission checks for process visibility, signal delivery, scheduling, debugging, socket visibility, and waiting.
- Implements credential allocation, copy, reference counting, COW synchronization, batching, group normalization, and process credential installation/removal.
- Implements login name get/set and credential field mutators.

## Credential Model
- `struct ucred` references are optimized with split `cr_users` and `cr_ref` accounting.
- Threads whose `td_realucred` matches the credential use `td_ucredref` to avoid frequent shared cache-line refcount traffic.
- `crcowget()`, `crcowfree()`, `crcowsync()`, `credbatch_add()`, and `credbatch_final()` manage COW and batched inactive-thread credential release.
- `crget()`, `crhold()`, `crfree()`, `crcopy()`, `crdup()`, `crcopysafe()`, and `crfree_final()` manage allocation and lifetime.
- `proc_set_cred()` and `proc_set_cred_enforce_proc_lim()` install process credentials and update process-count accounting.

## Group Handling
- Supplementary groups are normalized by sorting and duplicate removal in `groups_normalize()`.
- `group_is_supplementary()` uses binary search, relying on normalized groups.
- `groupmember()` checks effective GID plus supplementary groups; `realgroupmember()` checks real GID plus supplementary groups.
- `crsetgroups()`, `crsetgroups_internal()`, and `crsetgroups_and_egid()` update credential group arrays after `crextend()` ensures capacity.

## Security and Policy Hooks
- MAC hooks are integrated throughout setuid/setgid/setgroups/setcred, visibility, signaling, scheduling, debugging, socket visibility, and wait checks.
- Jail checks use `prison_check()` and parent-jail tamper rules via `cr_can_tamper_with_subjail()`.
- RACCT/RCTL hooks update accounting after credential changes.
- Debugging is controlled by `security.bsd.unprivileged_proc_debug`, `P_SUGID`, `P_INEXEC`, `P2_NOTRACE`, securelevel restrictions on `initproc`, and credential subset checks.
- Signal delivery is constrained by jail, MAC, BSD visibility, conservative `P_SUGID` signal policy, UID matching, and cross-jail tamper privilege.

## Key Interfaces
- Visibility: `cr_cansee()`, `p_cansee()`, `cr_bsd_visible()`, `cr_canseesocket()`.
- Permissions: `cr_cansignal()`, `p_cansignal()`, `p_cansched()`, `p_candebug()`, `p_canwait()`.
- Credentials: `crget()`, `crhold()`, `crfree()`, `crcopy()`, `crdup()`, `crcopysafe()`, `proc_set_cred()`, `proc_unset_cred()`.
- Identity mutators: `change_euid()`, `change_ruid()`, `change_svuid()`, `change_egid()`, `change_rgid()`, `change_svgid()`.
- Login/session: `sys_getlogin()`, `sys_setlogin()`, `setsugid()`.

## Notable Edge Cases
- Legacy FreeBSD 14 `getgroups`/`setgroups` compatibility treats effective GID as the first group.
- `kern_setcred()` builds the full new credential before MAC checks, then installs atomically under the process lock.
- Real UID changes can fail when process-count limits are enforced unless privilege overrides them.
- `crsetgroups()` accepts unsorted input and normalizes it before use.
- `allow_ptrace` is exposed as a tunable `security.bsd.allow_ptrace`.
