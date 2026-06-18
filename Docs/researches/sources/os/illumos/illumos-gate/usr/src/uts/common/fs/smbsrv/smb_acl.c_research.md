# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_acl.c

Kernel SMB ACL conversion and ACL utility implementation.

Key behavior:
- Allocates/frees SMB wire-format ACL structures and computes wire lengths.
- Validates ACL revision and ACE layout, currently rejecting object-specific ACL revision handling.
- Sorts DACL ACEs into Windows-preferred order using direct/inherited allow/deny groups.
- Converts ZFS `acl_t` ACE ACLs to Windows SMB ACLs using batched ID-to-SID mapping.
- Converts Windows SMB ACLs to ZFS ACLs using batched SID-to-ID mapping, handling well-known owner/group/everyone SIDs.
- Represents null and empty DACLs with synthetic ZFS ACLs.
- Allocates, frees, merges, and splits native filesystem ACLs.
- Implements Windows inheritance rules for new child objects, including creator owner/group handling and default DACL fallback.
- Converts between `vsecattr_t` and `acl_t`.
- Provides ACE type classification, generic-mask-to-file-specific translation, and flag conversion between Windows and ZFS forms.

Important dependencies:
- ID mapping: `smb_idmap_batch_create`, `smb_idmap_batch_getsid`, `smb_idmap_batch_getid`, `smb_idmap_batch_getmappings`.
- SID helpers: `smb_sid_dup`, `smb_sid_free`, `smb_sid_len`, `smb_sid_isvalid`, `smb_sid_tostr`.
- Solaris ACL helpers: `acl_alloc`, `acl_free`, `ace_trivial`, `ksort`, `cmp2acls`.

Notable details:
- Default inherited DACL grants owner and local system full access when no inheritable DACL exists.
- Empty DACL is simulated with owner implicit permissions rather than everyone-deny to avoid problematic deny precedence.
