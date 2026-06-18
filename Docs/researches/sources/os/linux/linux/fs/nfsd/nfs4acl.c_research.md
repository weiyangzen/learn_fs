# File Research: sources/os/linux/linux/fs/nfsd/nfs4acl.c

Read completely: 884 lines.

Common NFSD NFSv4 ACL translation code. It converts POSIX ACLs to NFSv4 ACLs for GETATTR/READ ACL paths and converts NFSv4 ACLs back to POSIX ACLs for SETATTR/write paths.

Key responsibilities:
- Defines NFSv4 ACL conversion flags for default ACLs, directories, and owner entries, plus supported permission and inheritance masks.
- Converts POSIX permissions to NFSv4 ALLOW/DENY masks, adding owner-specific and directory delete-child bits where appropriate.
- Builds an NFSv4 ACL from access and default POSIX ACLs in `nfsd4_get_nfs4_acl`, allocating worst-case deny/allow ACE pairs.
- Summarizes POSIX ACLs and emits ordered NFSv4 ACEs that preserve POSIX effective permissions using explicit DENY entries for permissions not granted by later entries.
- Sorts POSIX ACL USER/GROUP ranges by uid/gid before validation.
- Tracks NFSv4-to-POSIX conversion state with allow/deny bitmasks for owner, owning group, other, everyone, named users, named groups, and mask.
- Processes each NFSv4 ACE, rejects unsupported ACE types/flags, splits effective and default ACL state, and copies missing owner/group/other entries into default ACLs when inheritable entries exist.
- Converts accumulated state into POSIX ACLs and stores them in `struct nfsd_attrs` via `nfsd4_acl_to_attr`.
- Maps special NFSv4 who strings (`OWNER@`, `GROUP@`, `EVERYONE@`) to internal whotype values and writes them back to XDR.
- Provides `nfs4_acl_bytes` allocation sizing.

Dependencies:
- Uses POSIX ACL core helpers, nfsd ACL structures, idmapped nop mount context, NFSv4 constants, XDR stream encoding, and kernel uid/gid comparison helpers.

Notable risks:
- NFSv4 ACLs are richer than POSIX ACLs; conversion is necessarily lossy and errs restrictive when setting POSIX ACLs.
- Only ALLOW and DENY ACEs with a narrow supported flag set are accepted for conversion.
- State arrays allocate space for worst-case named users/groups based on ACE count; allocation failure must unwind both states.
- `ace2type` treats unknown whotypes as a kernel bug.
