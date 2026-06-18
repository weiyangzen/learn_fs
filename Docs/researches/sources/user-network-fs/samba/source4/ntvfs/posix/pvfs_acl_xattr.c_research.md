# sources/user-network-fs/samba/source4/ntvfs/posix/pvfs_acl_xattr.c

Purpose: registers a PVFS ACL backend named `xattr` that stores Samba `xattr_NTACL` security descriptors in native filesystem xattrs.

Important APIs and functions: `pvfs_acl_load_xattr` checks `PVFS_FLAG_XATTR_ENABLE`, reads `XATTR_NTACL_NAME` via `pvfs_xattr_ndr_load`, validates version `1`, and returns the embedded security descriptor. `pvfs_acl_save_xattr` wraps the SD in version `1`, elevates privileges, and writes via `pvfs_xattr_ndr_save`. `pvfs_acl_xattr_init` registers the backend.

Control flow: disabled xattrs behave as `NT_STATUS_NOT_FOUND`, allowing callers to fall back to default Unix-derived ACLs. Load failures free the temporary ACL wrapper. Save is a no-op success when xattrs are disabled; otherwise it writes to the system namespace under root privileges.

State and persistence: persisted state is the NDR-encoded `xattr_NTACL` xattr on each file. No process-global state exists except backend registration.

Dependencies and integration points: called through `pvfs_acl_ops` from `pvfs_acl.c`; depends on PVFS xattr helpers, generated `ndr_xattr` support, and privilege elevation.

Risks: disabled xattrs silently skip persistence on save; invalid versions return `NT_STATUS_INVALID_ACL`; root privilege boundaries and system-xattr support vary by platform. Test signals include disabled-xattr fallback, missing xattr, invalid version, save/load round trip, privilege failure, and integration with `pvfs_acl_query`/`pvfs_acl_set`.
