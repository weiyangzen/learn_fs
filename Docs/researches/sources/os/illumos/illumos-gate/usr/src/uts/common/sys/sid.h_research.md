# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/sid.h

## Role

Defines kernel SID/domain credential structures and userland SID/idmap syscall wrappers.

## Key Interfaces

- `sidsys` subcodes cover ID allocation, idmap registration/unregistration, kernel cache flush, SID-to-ID, and ID-to-SID operations.
- Kernel `ksiddomain_t` stores refcounted domain names in AVL trees.
- `ksid_t` combines cached UID/GID, RID, attributes, and domain pointer.
- `ksid_index_t` selects user, group, or owner SID slots.
- `ksidlist_t` stores refcounted SID arrays plus sorted ID pointers and ephemeral-ID count.
- `credsid_t` stores refcounted credential SID data and SID list.
- Kernel helpers manage lookup, holds/releases, credential SID updates, SID-list membership, and group-to-SID conversion.
- Userland exposes `allocids()`, `__idmap_reg()`, `__idmap_unreg()`, and `__idmap_flush_kcache()`.

## Risk Notes

SID credential substructures are refcounted because credential memory cannot be allocated while holding `p_crlock`. Incorrect hold/release behavior can corrupt credential SID state.
