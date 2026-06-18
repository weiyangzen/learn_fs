# File Research: sources/os/linux/linux/fs/ceph/util.c

Small non-inline Ceph utility helpers.

Functions:
- `ceph_file_layout_is_valid()`: validates stripe unit, stripe count, and object size constraints.
- `ceph_file_layout_from_legacy()`: decodes legacy little-endian layout fields into `ceph_file_layout`, treating all-zero legacy layout as pool `-1`.
- `ceph_file_layout_to_legacy()`: encodes current layout into legacy structure, writing pool 0 for negative pool IDs.
- `ceph_flags_to_mode()`: converts open flags into Ceph file modes, with special handling for `O_DIRECTORY` as pin mode and optional `O_LAZY`.
- `ceph_caps_for_mode()`: maps Ceph file mode bits to required capability bits.

Important behavior:
- Layout validation enforces nonzero stripe unit/object size, 64 KiB alignment, object size multiple of stripe unit, and nonzero stripe count.
- Write mode implies file write/buffer caps plus auth and xattr shared/exclusive caps.
- Lazy mode adds `CEPH_CAP_FILE_LAZYIO`.
