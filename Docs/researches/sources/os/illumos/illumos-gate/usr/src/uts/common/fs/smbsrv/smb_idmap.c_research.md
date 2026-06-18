# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_idmap.c

## Role

Kernel SMB interface to illumos ID mapping, translating between Unix UID/GID values and Windows SIDs through `kidmap`.

## Major Responsibilities

- Maps UID/GID to binary SMB SIDs.
- Maps binary SMB SIDs to UID/GID or unknown principal type.
- Provides batch mapping contexts for groups of ID/SID conversions.
- Handles special SMB identities such as Everyone, current owner, and current group.
- Converts returned domain SID strings plus RIDs into binary SID objects.
- Frees batch-allocated SID/domain state correctly for each mapping direction.

## Key Functions

- `smb_idmap_getsid()` maps one UID/GID/special ID to an SMB SID using `kidmap_getsidbyuid()` or `kidmap_getsidbygid()`.
- `smb_idmap_getid()` splits a SID into domain SID and RID and maps it to UID, GID, or principal type.
- `smb_idmap_batch_create()` initializes a `kidmap` batch handle and allocates map entries.
- `smb_idmap_batch_destroy()` destroys the batch handle and frees direction-specific allocations.
- `smb_idmap_batch_getid()` queues SID-to-ID lookups.
- `smb_idmap_batch_getsid()` queues ID-to-SID lookups and handles special SID constants.
- `smb_idmap_batch_getmappings()` runs queued mappings, counts/report errors, optionally skips errors, and converts SID/RID pairs to binary SIDs.
- `smb_idmap_batch_binsid()` builds binary SIDs for ID-to-SID batch results.

## Research Notes

Unlike user-level SMB idmap helpers, this kernel implementation calls `kidmap_*` directly and treats returned domain SID strings as shared state except where SID-to-ID batching duplicates strings for later cleanup.
