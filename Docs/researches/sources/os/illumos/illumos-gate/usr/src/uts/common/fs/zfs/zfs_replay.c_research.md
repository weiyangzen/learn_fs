# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/zfs_replay.c

Implements replay of ZFS Intent Log records for ZPL operations. The file translates logged record payloads from `zfs_log.c` back into vnode/ZPL operations after a crash or replay event, using a transaction-type vector indexed by ZIL transaction type.

Key elements:
- `zfs_init_vattr()` reconstructs a `vattr_t` from logged mode, UID/GID, rdev, and node ID, treating ephemeral IDs as unset vnode IDs.
- `zfs_replay_xvattr()` unpacks logged xvattr bitmaps, flags, create time, AV scanstamp or project ID, and extended attribute booleans.
- FUID helpers reconstruct replay-time domain tables and FUID lists: `zfs_replay_domain_cnt()`, `zfs_replay_fuid_domain_common()`, `zfs_replay_fuid_ugid()`, `zfs_replay_fuid_domain()`, and `zfs_replay_fuids()`.
- `zfs_replay_swap_attrs()` byteswaps variable-size xvattr payloads for logs written on opposite-endian systems.
- `zfs_replay_create_acl()` replays ACL-bearing creates and mkdirs, claims the logged object/dnode slots, reconstructs ACL and FUID replay state, and calls `VOP_CREATE()` or `VOP_MKDIR()`.
- `zfs_replay_create()` replays normal create, mkdir, xattr-directory creation, symlink, and attr-bearing create/mkdir records.
- `zfs_replay_remove()`, `zfs_replay_link()`, and `zfs_replay_rename()` replay namespace operations through vnode operations with case-insensitive flags when logged.
- `zfs_replay_write()` replays write records, dropping writes to already-removed files, handling full-block dmu-sync records, and using `z_replay_eof` to preserve file-size semantics.
- `zfs_replay_write2()` handles delayed EOF extension for `TX_WRITE2` records by updating SA size in a DMU transaction.
- `zfs_replay_truncate()` replays truncation/free-space operations through `VOP_SPACE()`.
- `zfs_replay_setattr()` replays vnode attributes, xvattrs, and FUID domain context through `VOP_SETATTR()`.
- `zfs_replay_acl_v0()` and `zfs_replay_acl()` replay legacy and FUID-aware ACL records through `VOP_SETSECATTR()`.
- `zfs_replay_vector[]` maps all supported transaction types to their replay handlers and maps unsupported entries to `zfs_replay_error()`.

Main dependencies and interactions:
- Consumes the exact record formats produced by `zfs_log.c`, including create/ACL/xvattr/FUID packing and dnode-slot encoding.
- Calls ZPL vnode operations so replay follows normal filesystem mutation paths while using `kcred`.
- Uses `dnode_try_claim()` to recreate logged object IDs and large-dnode slot counts.
- Temporarily stores FUID replay context on `zfsvfs->z_fuid_replay` so lower-level create/setattr/ACL paths can resolve identities.
- Updates ZIL replay sequence state through `zil_replaying()` when replay creates its own DMU transaction in `zfs_replay_write2()`.

Implementation notes:
- Most handlers byteswap fixed record headers first, then byteswap variable sections such as ACLs, FUID arrays, and xvattr payloads using logged lengths.
- Create replay smuggles logged creation time, generation number, and dnode size through otherwise unused `vattr_t` fields because generic create vnode operations do not expose those ZFS-specific values.
- Write replay treats missing file objects as success for ordinary writes because log records may be replayed out of order relative to remove records.
- `z_replay_eof` is set only around replayed full-block writes that extend past current EOF and is cleared immediately after the write path.
- Each handler releases vnodes it acquired and frees temporary FUID replay state before returning.

Risk/attention points:
- Replay correctness depends on strict agreement with `zfs_log.c` record layout, especially variable xvattr and ACL/FUID offsets.
- Endian conversion must happen before interpreting variable sizes; mistakes can mislocate names, ACLs, or domain strings.
- The create replay path claims exact object IDs and dnode slot counts; failure there prevents faithful replay of later records targeting those IDs.
