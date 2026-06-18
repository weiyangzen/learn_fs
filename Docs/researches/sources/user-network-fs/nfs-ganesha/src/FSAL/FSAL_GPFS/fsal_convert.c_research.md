# sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_GPFS/fsal_convert.c

Purpose: this file translates GPFS-specific xstat, ACL, credential, and mode representations into Ganesha FSAL structures and back. It is the conversion layer used by GPFS getattr, setattr, access, and ACL paths.

Important APIs and functions: `gpfsfsal_xstat_2_fsal_attributes()` fills requested FSAL attributes from `gpfsfsal_xstat_t`, including type, size, FSID, ACL, fileid, mode, links, owner/group, atime/ctime/mtime, change, space used, and rawdev. `gpfs_acl_2_fsal_acl()` converts GPFS NFSv4 ACL entries into FSAL ACEs and creates a cached `fsal_acl_t`. `fsal_acl_2_gpfs_acl()` converts FSAL ACEs into a GPFS `gpfs_acl_t` buffer and validates maximum ACE count plus inheritance rules. `fsal_cred_2_gpfs_cred()` maps caller uid/gid/groups. `fsal_mode_2_gpfs_mode()` converts FSAL mode or NFSv4 access mask into GPFS access mode bits.

Control flow: attribute conversion is request-mask driven, so only requested attrs are filled and marked valid. ACL conversion is attempted only when requested, enabled, and present in `attr_valid`; failure to provide a requested ACL fails the whole conversion. Change time is computed as the greater of mtime/ctime with nanosecond handling. Mode conversion derives read/write/execute bits from NFSv4 ACE permissions when an explicit mode is zero.

State and persistence: this file does not persist data itself. It allocates FSAL ACL entries through the NFSv4 ACL cache and writes caller-provided GPFS ACL buffers. The resulting attrlists and ACLs are consumed by higher FSAL layers.

Dependencies and integration: it depends on `fsal_internal.h`, GPFS ACL constants, `nfs4_acls.h`, POSIX stat types, and FSAL ACE helper macros. It is called directly from `fsal_attrs.c` and access-related GPFS code.

Risks and test signals: `fsal_cred_2_gpfs_cred()` copies groups without checking GPFS array capacity in this file. `fsal_mode_2_gpfs_mode()` shifts mode by 24 bits, so callers must pass FSAL-mode formatted masks. ACL inheritance validation rejects inherit flags on non-directories and inherit-only without inherit flags, which should be reflected in client errors. Tests should cover request-mask partial attr conversion, ACL disabled/missing cases, special owner/group ACE conversion, max ACE overflow, invalid inheritance combinations, change time ordering with nanoseconds, credential group copying, and mode conversion from both explicit mode and v4 masks for files/directories.
