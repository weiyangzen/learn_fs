# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/policy.c

## Purpose

`policy.c` contains the main illumos kernel privilege and security-policy checks. It maps kernel operations to privileges, handles auditing and privilege-debug reporting, supports external policy overrides, and implements policy wrappers for filesystems, vnodes, IPC, processes, devices, networking, zones, contracts, and storage-adjacent subsystems.

Read completely: 2,671 lines.

## Main Responsibilities

- Implements bottom-level privilege checks through `priv_policy*()` helpers.
- Emits audit records and privilege-debug messages for failed or successful privileged operations.
- Supports external policy through KLPD and PFEXEC privilege override paths.
- Encodes special root and zone escalation rules.
- Defines filesystem mount, unmount, quota, vnode access, setattr, setid, chown, and extended-attribute policies.
- Defines policy checks for IPC, auditing, process control, resource control, device access, module control, networking, contracts, graphics, ZFS, SMB, vscan, xVM, and PPP.

## Privilege Core

The file defines helper macros over credential privilege sets:

- `HAS_ALLPRIVS()`
- `ZONEPRIVS()`
- `HAS_ALLZONEPRIVS()`
- `HAS_PRIVILEGE()`
- `FAST_BASIC_CHECK()`

The comments distinguish three policy patterns: requiring one privilege, requiring one privilege plus all zone privileges, and requiring all privileges globally.

`priv_policy_ap()` is the core check. It grants access if the credential has the requested privilege and required zone privileges, or if external policy approves. On success it may mark accounting `ASU` and audit success. On failure it audits and reports missing privilege information when appropriate.

`priv_policy()`, `priv_policy_va()`, `priv_policy_choice()`, and `priv_policy_only()` provide error-returning, varargs, boolean/auditing, and boolean/non-auditing variants.

`secpolicy_require_set()` checks an arbitrary privilege set, handles PFEXEC/KLPD overrides, audits missing sets, and reports either the single missing privilege or `PRIV_MULTIPLE`.

`priv_policy_global()` requires global-zone execution regardless of privilege.

## Debugging, Auditing, and Overrides

`priv_policy_errmsg()` records missing privilege details in `lwp_badpriv` and optional `t_pdmsg`, and can log kernel notes under `priv_debug`. It tries to identify the first useful caller outside common policy wrappers.

`priv_policy_override()` calls KLPD for a single requested privilege or zone/all-privilege set when `PRIV_XPOLICY` is set.

`priv_policy_override_set()` supports PFEXEC checks with `check_user_privs()` and KLPD set checks.

`priv_policy_err()` emits audit failure and DTrace probes, then optionally calls `priv_policy_errmsg()`.

## Filesystem Mount Policy

`secpolicy_fs_common()` is the central mount ownership check. It handles pure privilege checks, zone restrictions for existing mounts, overlay-mount escalation checks, mount-point ownership and write access, and the all-zone privilege requirement for sensitive cases.

`secpolicy_fs_mount()` handles remount mount-point selection and invokes `secpolicy_fs_mount_clearopts()` when mount options must be restricted.

`secpolicy_fs_mount_clearopts()` enforces `nosuid`, `nodevices`, and `restrict` behavior depending on zone and privilege state.

`secpolicy_fs_allowed_mount()` lets non-global zones mount only filesystem types marked `VSW_ZMOUNT` or listed in `zone_fs_allowed`.

`secpolicy_fs_unmount()`, `secpolicy_fs_quota()`, `secpolicy_fs_minfree()`, and `secpolicy_fs_config()` reuse mount ownership policy.

`secpolicy_fs_linkdir()` blocks directory hard-link/unlink by default unless `priv_allow_linkdir` is set.

## Vnode and Attribute Policy

`secpolicy_vnode_access()` and `secpolicy_vnode_access2()` map denied read, write, execute, and directory search access to DAC and basic file privileges. Writes to root-owned objects can require all zone privileges.

`secpolicy_vnode_any_access()` is a ZFS-oriented non-auditing probe that checks whether any effective privilege would allow file access.

Setid and ownership helpers include `secpolicy_vnode_setid_modify()`, `secpolicy_vnode_setid_retain()`, `secpolicy_vnode_setids_setgids()`, `secpolicy_vnode_chown()`, `secpolicy_vnode_create_gid()`, `secpolicy_vnode_setdac()`, `secpolicy_vnode_setdac3()`, `secpolicy_vnode_stky_modify()`, `secpolicy_vnode_remove()`, `secpolicy_vnode_owner()`, `secpolicy_setid_clear()`, and `secpolicy_setid_setsticky_clear()`.

`secpolicy_xvattr()` checks optional attributes. DOS-style bits require ownership; immutable, nounlink, append-only, nodump, antivirus quarantine/modified/scanfstamp require file flag privileges or all privileges for clearing; opaque is rejected; some AV attributes are valid only on regular files.

`secpolicy_vnode_setattr()` is the main setattr policy helper. It handles size changes, mode changes, setid/sticky clearing, chown/chgrp rules, timestamp updates, ACL-check skipping, owner implicit rights, and extended attributes.

`secpolicy_pcfs_modify_bootpartition()` requires all privileges to modify a pcfs boot partition.

## IPC, Audit, and Process Policy

System V IPC policy includes `secpolicy_ipc_owner()`, `secpolicy_ipc_config()`, `secpolicy_ipc_access()`, and `secpolicy_rsm_access()`, with root-owned IPC write cases requiring all zone privileges.

Audit policy includes `secpolicy_audit_config()`, `secpolicy_audit_modify()`, and `secpolicy_audit_getattr()`.

Process and resource policy includes `secpolicy_lock_memory()`, `secpolicy_acct()`, `secpolicy_allow_setid()`, `secpolicy_proc_owner()`, `secpolicy_proc_access()`, `secpolicy_proc_excl_open()`, `secpolicy_proc_zone()`, `secpolicy_kmdb()`, `secpolicy_error_inject()`, `secpolicy_psecflags()`, `secpolicy_chroot()`, `secpolicy_tasksys()`, `secpolicy_meminfo()`, and basic exec/fork/session/procinfo/link/network/file read/write checks.

CPU and resource controls include `secpolicy_pset()`, `secpolicy_pbind()`, `secpolicy_ponline()`, `secpolicy_pool()`, `secpolicy_blacklist()`, `secpolicy_sys_config()`, `secpolicy_zone_admin()`, `secpolicy_zone_config()`, `secpolicy_rctlsys()`, `secpolicy_resource()`, `secpolicy_resource_anon_mem()`, and `secpolicy_newproc()`.

## Device, Module, and Hardware Policy

`drv_priv()`, `secpolicy_sys_devices()`, `secpolicy_excl_open()`, `secpolicy_console()`, and `secpolicy_power_mgmt()` map device operations to `PRIV_SYS_DEVICES`.

`secpolicy_spec_open()` enforces device policy privilege sets cached in snodes. It refreshes stale device policy generations, selects read or write privilege sets, and treats `PRIV_SYS_NET_CONFIG` as a superset of `PRIV_SYS_IP_CONFIG` for device-policy checks.

`secpolicy_modctl()` allows informational module commands unprivileged, requires all privileges for module loading and device policy setting, and otherwise falls back to system configuration privilege.

High-risk hardware paths include `secpolicy_sti()`, `secpolicy_cpc_cpu()`, `secpolicy_gart_access()`, `secpolicy_gart_map()`, `secpolicy_hwmanip()`, `secpolicy_zinject()`, and `secpolicy_ucode_update()`.

## Networking Policy

Networking checks include privileged port binding, MLP/MAC policies, raw access, observability, ICMP access, net/IP/datatalink/tunnel configuration, NFS, rpcmod, SAD admin device access, and PPP configuration.

`secpolicy_net_privaddr()` special-cases SMB/NBT ports for `PRIV_SYS_SMB` or `PRIV_NET_PRIVADDR`, NFS ports for `PRIV_SYS_NFS`, and all other privileged ports for `PRIV_NET_PRIVADDR`.

`secpolicy_ip_config()`, `secpolicy_dl_config()`, `secpolicy_iptun_config()`, and `secpolicy_ppp_config()` encode privilege supersets so broader network privileges satisfy narrower subsystem configuration checks.

`secpolicy_ip()` and `secpolicy_net()` map pseudo privileges such as `OP_CONFIG`, `OP_RAW`, and `OP_PRIVPORT` to concrete privileges.

## Storage and Filesystem Adjacent Policies

`secpolicy_zfs()` maps ZFS dataset manipulation to `PRIV_SYS_MOUNT`.

`secpolicy_zinject()` requires the full privilege set for ZFS fault injection.

`secpolicy_swapctl()` uses `PRIV_SYS_CONFIG`.

`secpolicy_smb()` protects SMB server driver access with `PRIV_SYS_SMB`.

`secpolicy_vscan()` requires DAC search, DAC read, and file flag setting for virus scanning.

`secpolicy_smbfs_login()` permits a user to manage their own SMBFS login and requires process-owner privilege for others.

## Contracts and Miscellaneous

Contract checks include `secpolicy_contract_identity()`, `secpolicy_contract_observer()`, `secpolicy_contract_observer_choice()`, `secpolicy_contract_event()`, and `secpolicy_contract_event_choice()`.

Other targeted checks include `secpolicy_idmap()`, `secpolicy_pfexec_register()`, `secpolicy_net_reply_equal()`, and `secpolicy_xvm_control()`.

## Notable Invariants

- Policy functions must not assume any particular lock state.
- Credentials are treated as read-only.
- Root-owned files and root identity transitions often require more than a single narrow privilege to prevent escalation.
- Zone operations that can expand available privileges require all privileges available in the zone or all privileges in the global zone.
- Many check-only variants return `0` for allowed and `EPERM` or boolean inverse forms for denied, so callers must observe each function's convention.

## Research Relevance

This is a core filesystem-security file. It defines mount restrictions, vnode permission overrides, setuid/setgid preservation, extended attributes, device policy, ZFS permissions, swap control, SMB/vscan policy, and zone privilege boundaries. Filesystem code in illumos commonly delegates authorization decisions here rather than open-coding privilege checks.
