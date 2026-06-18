# File Research: sources/os/linux/linux-stable/fs/ceph/ioctl.c

## Role

`ioctl.c` implements CephFS-specific ioctl handling plus fscrypt ioctl forwarding that requires CephFS/MDS feature checks. It maps user ABI structures from `ioctl.h` to Ceph layout metadata, MDS requests, OSD placement calculations, and file consistency flags.

## Layout Ioctls

`ceph_ioctl_get_layout()` refreshes layout metadata with `ceph_do_getattr(..., CEPH_STAT_CAP_LAYOUT, false)`, copies the current inode layout into `struct ceph_ioctl_layout`, sets obsolete `preferred_osd` to `-1`, and copies it to userspace.

`__validate_layout()` validates object size and stripe unit alignment to page size, validates `object_size % stripe_unit`, and checks that `data_pool` is present in the current MDS map data pools under `mdsc->mutex`.

`ceph_ioctl_set_layout()` copies user layout, fetches current layout, fills unspecified fields from current inode layout, validates the resulting layout, builds a `CEPH_MDS_OP_SETLAYOUT` request, drops file shared/excl caps, and sends it to the auth MDS.

`ceph_ioctl_set_layout_policy()` validates a directory layout policy and sends `CEPH_MDS_OP_SETDIRLAYOUT`, causing future descendants to inherit the policy unless overridden.

## Data Location Ioctl

`ceph_ioctl_get_dataloc()` maps a file offset to Ceph object and OSD placement details.

It:

- Copies `struct ceph_ioctl_dataloc` from userspace.
- Uses `ceph_calc_file_object_mapping()` to compute object number, object offset, object size, and stripe unit.
- Builds the object name as `<ino>.<object_no>`.
- Constructs a `ceph_object_locator` with pool id and pool namespace.
- Converts object locator to PG and then to acting primary OSD under `osdc->lock`.
- Copies the OSD network address if available.
- Copies the populated structure back to userspace.

## Lazy And Sync I/O Flags

`ceph_ioctl_lazyio()` marks a file descriptor as lazy via `CEPH_FILE_MODE_LAZY`, increments the per-inode lazy mode counter when first set, touches fmode state, and triggers `ceph_check_caps()` when the file newly becomes lazy.

`ceph_ioctl_syncio()` sets `CEPH_F_SYNC` in `struct ceph_file_info`, forcing sync/direct-like behavior for that file descriptor.

## Fscrypt Support

`vet_mds_for_fscrypt()` checks active MDS sessions for `CEPHFS_FEATURE_ALTERNATE_NAME`, returning `-EOPNOTSUPP` when the feature is unavailable.

`ceph_set_encryption_policy()` rejects encrypted policy setup on directories with striped layout (`stripe_count > 1`), verifies MDS fscrypt support, obtains `CEPH_CAP_FILE_SHARED` so empty-directory checks are reliable, calls `fscrypt_ioctl_set_policy()`, and releases cap refs.

The dispatch path also vets MDS feature support before fscrypt policy get, extended policy get, add key, and nonce retrieval. Key removal and key-status ioctls are passed through without the same feature gate in this file.

## Dispatch

`ceph_ioctl_cmd_name()` maps known commands to debug names.

`ceph_ioctl()` logs the command and dispatches:

- `CEPH_IOC_GET_LAYOUT`
- `CEPH_IOC_SET_LAYOUT`
- `CEPH_IOC_SET_LAYOUT_POLICY`
- `CEPH_IOC_GET_DATALOC`
- `CEPH_IOC_LAZYIO`
- `CEPH_IOC_SYNCIO`
- fscrypt policy/key/nonce ioctls

Unknown commands return `-ENOTTY`.

## Error Handling

- Bad userspace copies return `-EFAULT`.
- Invalid layout values or pools return `-EINVAL`.
- Missing fscrypt MDS support returns `-EOPNOTSUPP`.
- MDS request allocation errors propagate through `PTR_ERR()`.
- Dataloc placement conversion errors propagate from `ceph_object_locator_to_pg()`.
