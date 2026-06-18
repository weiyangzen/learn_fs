# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/zfs_log.c

Builds ZFS Intent Log records for filesystem namespace, data, attribute, and ACL operations. The functions are called while a DMU transaction is active; in normal operation they allocate and assign in-memory intent transactions, while replay mode suppresses new logging.

Key elements:
- `zfs_log_create_txtype()` maps create kind plus ACL/xvattr presence to ZIL transaction types such as `TX_CREATE`, `TX_CREATE_ACL_ATTR`, `TX_MKDIR_ATTR`, and `TX_MKXATTR`.
- `zfs_log_xvattr()` packs requested extended attributes, create time, AV scanstamp or project ID, and attribute flags into a ZIL `lr_attr_t` payload.
- `zfs_log_fuid_ids()` and `zfs_log_fuid_domains()` append FUID and domain replay data.
- `zfs_log_create()` logs file, directory, xattr-directory, ACL-create, and xvattr-create records, including object ID, dnode slot count, mode, UID/GID/FUID, generation, create time, rdev, ACL data, FUID data, and name.
- `zfs_log_remove()` logs remove/rmdir and purges async write records for unlinked objects to avoid stale object-id reuse leaks.
- `zfs_log_link()`, `zfs_log_symlink()`, and `zfs_log_rename()` log namespace link, symlink, and rename operations.
- `zfs_log_write()` logs writes as indirect, copied, or need-copy records based on log bias, slog availability, write size, and commit semantics.
- `zfs_log_truncate()` logs file space truncation/free operations.
- `zfs_log_setattr()` logs setattr payloads, including xvattr and FUID domain data when needed.
- `zfs_log_acl()` logs legacy ACL v0 records for old ZPL versions or modern FUID-aware ACL records for newer filesystems.

Main dependencies and interactions:
- Paired with `zfs_replay.c`, whose replay vector interprets these record layouts.
- Depends on znode state, SA attributes, vnode attributes, ACL structures, FUID structures, DMU reads, ZIL intent transaction allocation, and SPA slog/log-bias state.
- Called by ZPL vnode/directory operations after metadata/data mutation decisions have been made.

Implementation notes:
- All public logging helpers immediately return when `zil_replaying(zilog, tx)` is true; replayed operations update replay state instead of recursively logging.
- Create records encode dnode slot count into high bits of `lr_foid` with `LR_FOID_SET_SLOTS()`, preserving large-dnode replay.
- `zfs_log_write()` splits indirect writes on block boundaries and limits copied payloads to `ZIL_MAX_COPIED_DATA`; failed immediate data reads fall back to `WR_NEED_COPY`.
- `itx->itx_sync` is set for write/truncate/setattr/ACL records when the znode has synchronous waiters.
- FUID replay data is optional and appended only when ephemeral identities or ACL FUIDs require domain reconstruction.

Risk/attention points:
- The packed xvattr layout must stay synchronized with `zfs_replay_xvattr()` in `zfs_replay.c`; mismatched offsets would corrupt replayed attributes.
- The ACL/FUID record sizes include padding via `ZIL_ACE_LENGTH()`, which replay depends on for locating FUID arrays and domain strings.
- `zfs_log_xvattr()` appears to encode `XAT_OPAQUE` using `XAT0_APPENDONLY`; replay expects `XAT0_OPAQUE`, so this is a notable compatibility/bug-sensitive area when auditing attribute replay behavior.
