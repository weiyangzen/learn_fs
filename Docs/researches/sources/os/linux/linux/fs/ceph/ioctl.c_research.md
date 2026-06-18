# File Research: sources/os/linux/linux/fs/ceph/ioctl.c

## Purpose

`ioctl.c` implements CephFS file ioctl handling. It supports layout inspection and changes, data-location queries, lazy/sync I/O mode flags, and forwarding of fscrypt policy/key ioctls with Ceph-specific MDS feature checks.

## Major Interfaces

- `ceph_ioctl()` is the exported dispatcher for all supported ioctl commands.
- `ceph_ioctl_get_layout()` returns file or directory layout fields.
- `ceph_ioctl_set_layout()` sends `CEPH_MDS_OP_SETLAYOUT` for file layout changes.
- `ceph_ioctl_set_layout_policy()` sends `CEPH_MDS_OP_SETDIRLAYOUT` for directory layout inheritance policy.
- `ceph_ioctl_get_dataloc()` maps a file offset to object name, object offsets, PG primary OSD, and OSD address.
- `ceph_ioctl_lazyio()` marks the open file mode as lazy and triggers cap recheck.
- `ceph_ioctl_syncio()` sets `CEPH_F_SYNC` in the file private flags.
- `ceph_set_encryption_policy()` wraps `fscrypt_ioctl_set_policy()` with Ceph layout and MDS feature validation.

## Layout Operations

`ceph_ioctl_get_layout()` refreshes layout caps via `ceph_do_getattr(..., CEPH_STAT_CAP_LAYOUT, false)`, copies current `ci->i_layout` fields to `struct ceph_ioctl_layout`, forces obsolete `preferred_osd` to `-1`, and copies the structure to user memory.

`__validate_layout()` rejects object size or stripe unit values that are not page aligned and rejects object sizes not divisible by stripe unit. It also checks `mdsc->mdsmap->m_data_pg_pools` under `mdsc->mutex` to ensure the requested data pool is valid.

`ceph_ioctl_set_layout()` copies user input, fetches current layout, treats zero fields as "keep current", validates the effective layout, creates a `CEPH_MDS_OP_SETLAYOUT` request, attaches the inode and cap count, drops file shared/exclusive caps, fills legacy layout fields, executes the request, and releases it.

`ceph_ioctl_set_layout_policy()` validates user-provided layout directly, creates `CEPH_MDS_OP_SETDIRLAYOUT`, fills layout fields, and sends the request against the directory inode.

## Data Location Query

`ceph_ioctl_get_dataloc()` copies a `struct ceph_ioctl_dataloc` from userspace and computes the Ceph object mapping for `file_offset` with `ceph_calc_file_object_mapping()`. Under the OSD client read lock, it:

- computes object number and object offset;
- normalizes `file_offset` to the object's start offset;
- fills object and block sizes;
- computes block offset with `do_div`;
- formats object name as `<ino>.<object_no>`;
- builds an object locator from layout pool and namespace;
- maps object locator to PG;
- resolves acting primary OSD and copies its address when available.

It then copies the filled structure back to userspace.

## Lazy And Sync I/O Flags

`ceph_ioctl_lazyio()` sets `CEPH_FILE_MODE_LAZY` on the file private mode if not already set, increments the inode per-mode count, touches file mode state for cap tracking, and calls `ceph_check_caps()` after releasing `i_ceph_lock`.

`ceph_ioctl_syncio()` sets `CEPH_F_SYNC` in `struct ceph_file_info`, forcing synchronous Ceph I/O behavior for that file descriptor.

## Fscrypt Ioctls

`vet_mds_for_fscrypt()` checks active MDS sessions for `CEPHFS_FEATURE_ALTERNATE_NAME`. The dispatcher gates most fscrypt policy/key/status/nonce ioctls through this check before calling generic fscrypt ioctl helpers.

`ceph_set_encryption_policy()` additionally rejects directories with striped layout (`stripe_count > 1`), obtains `CEPH_CAP_FILE_SHARED` to make empty-directory checks reliable, calls `fscrypt_ioctl_set_policy()`, and drops cap refs afterward.

## Dispatch

`ceph_ioctl_cmd_name()` maps known commands to names for debug logging. `ceph_ioctl()` logs file, inode, vino, command name, and arg, then switches over Ceph-specific and fscrypt commands. Unknown commands return `-ENOTTY`.

## Dependencies

The file depends on Ceph MDS request APIs, Ceph layout/striper helpers, OSD map helpers, file private state, cap tracking, and Linux user-copy/fscrypt ioctl APIs.

## Error Handling And Risks

- User memory failures return `-EFAULT`.
- Invalid layout parameters or unknown data pools return `-EINVAL`.
- MDS request creation failures propagate pointer errors.
- Data location queries assume `dl.block_size` from layout stripe unit is non-zero before `do_div`; layout invariants should guarantee this for valid files.
- `vet_mds_for_fscrypt()` breaks after the first non-null session, so behavior depends on the first active session's advertised features.
- Layout setting sends user-provided fields, not the normalized `nl` values, allowing zero fields to mean unchanged in the MDS protocol; this should remain aligned with MDS semantics.
