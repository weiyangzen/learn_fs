# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/sid.c

Implements kernel SID and SID-list support used by credentials. Despite the file comment calling these “stubs,” the file contains real domain interning, refcounting, credential SID copy-on-write, lookup helpers, and sorted membership checks.

Key responsibilities:
- Interns SID domain strings in a global AVL tree protected by `sid_lock`.
- Maintains atomic reference counts for `ksiddomain_t`, `ksidlist_t`, and `credsid_t`.
- Provides hold/release helpers for individual SIDs, SID lists, and credential SID containers.
- Supports UID/GID to SID lookup through kernel idmap functions when `_KERNEL` is enabled.
- Converts oversized POSIX GIDs into SIDs for credential supplemental groups.

Important paths:
- `ksid_lookupdomain()` lazily initializes `sid_tree`, finds or creates a domain, and returns it held.
- `ksiddomain_rele()` removes and frees a domain only after the atomic refcount reaches zero and a locked recheck confirms it.
- `ksidlist_has_sid()` searches by RID/domain, using linear search for small lists and binary search for larger sorted lists.
- `ksidlist_has_pid()` searches POSIX IDs through `ksl_sorted`, the pointer array sorted by `ks_id`.
- `kcrsid_dup()` implements copy-on-write for credential SID metadata.
- `kcrsid_setsid()` updates one indexed SID while preserving or dropping the auxiliary structure when empty.
- `kcrsid_setsidlist()` installs a SID list and sorts it both by SID and POSIX ID.
- `kcrsid_gidstosids()` builds a SID list from supplemental groups above `MAXUID`.

Memory and locking model:
- Domain AVL tree mutations require `sid_lock`.
- Object lifetime is atomic-refcount based.
- `kcrsid_dup()` may return the original object when uniquely owned, so callers must treat returned pointers as the authoritative object.
- `kcrsid_setsidlist()` assumes the incoming list already carries proper held domain references and a reference count including the new owner.

Filesystem relevance:
- SID metadata is part of credential identity and access-control plumbing. It matters to filesystem research where Windows-compatible ACLs, SMB/NFS identity mapping, or ZFS/illumos ACL decisions depend on kernel credentials containing SID state.
