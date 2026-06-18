# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/policy.h

## Purpose
Declares kernel security policy and privilege-check routines used across filesystems, networking, process control, zones, devices, ZFS, auditing, and resource management.

## Main Interfaces
- Generic policy checks:
  - `priv_policy()`
  - `priv_policy_only()`
  - `priv_policy_choice()`
  - `PRIV_POLICY`
  - `PRIV_POLICY_CHOICE`
  - `PRIV_POLICY_ONLY`
- Large family of `secpolicy_*()` checks for:
  - auditing, clock, contracts, coreadm, CPC, error injection, modctl, kmdb
  - filesystem mount/unmount/quota/linkdir/minfree and vnode access/setattr/chown/setid/sticky policies
  - IPC, NFS, PPP, SMB/SMBFS, RPC module open
  - networking, raw access, privileged ports, MAC awareness/implicit policies, observability
  - process access, owner checks, zones, processor binding/sets/online, priority, resource controls
  - power management, pools, tasks, devices, system info/configuration, ZFS, `zinject`, ucode updates
- `secpolicy_vnode_setattr()`: combined vnode setattr policy helper that may alter `va_mask`.
- `in_port_t` definition guard for kernel use.

## Dependencies And Relationships
Kernel-only declarations guarded by `_KERNEL`. Includes credentials, vnodes, and snode support; forward-declares several subsystem types. It centralizes policy entry points used by many kernel modules.

## Research Notes
The three generic privilege helpers differ in auditing/debugging behavior. Callers must choose the variant appropriate for normal, choice-style, or interrupt-context checks.
