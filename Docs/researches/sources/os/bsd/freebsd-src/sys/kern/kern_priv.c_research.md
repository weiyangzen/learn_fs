# File Research: sources/os/bsd/freebsd-src/sys/kern/kern_priv.c

Read completely: 366 lines.

## Purpose
Implements centralized kernel privilege checks, combining MAC policy denial/grant hooks, jail restrictions, configurable superuser policy, special unprivileged allowances, and fast paths for common VFS privileges.

## Main Elements
- `suser_enabled()` checks the jail/prison `PR_ALLOW_SUSER` policy.
- `sysctl_kern_suser_enabled()` exposes and updates `security.bsd.suser_enabled` per prison.
- Sysctls control unprivileged `mlock`/`munlock` and unprivileged kernel message-buffer reads.
- SDT probes report successful and failed privilege checks.
- `priv_check_cred_pre()` calls MAC denial hooks when enabled.
- `priv_check_cred_post()` gives MAC grant hooks a final chance and otherwise defaults to `EPERM`.
- `priv_check_cred()` handles special VFS fast-path dispatch, MAC precheck, jail restriction, unprivileged allowances, superuser grants by effective or real uid, special kernel memory/process memory allowances, and unprivileged debug policy.
- `priv_check()` checks the current thread's credentials.
- `priv_check_cred_vfs_lookup()` and `_nomac()` provide optimized root/superuser checks unless MAC/probes require the slow path.
- `priv_check_cred_vfs_generation()` denies jailed callers and otherwise permits root when superuser policy is enabled.

## Dependencies And Integration
Uses credentials, jail/prison policy, MAC framework hooks, SDT probes, sysctl, privilege constants, and VFS-specific privilege helpers. Many files in this group call into it indirectly, including NTP time adjustment and filesystem/VFS metadata checks.

## Risk Notes
The default policy is deny unless a specific path grants privilege. Disabling superuser semantics can break traditional root assumptions. Fast paths intentionally bypass MAC only when MAC hooks/probes are inactive; otherwise they return slow-path results or `EAGAIN` for the nomac variant.
