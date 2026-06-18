# sources/test-tools/strace/bundled/linux/include/uapi/linux/nsfs.h

## Purpose

Defines the userspace ABI for namespace filesystem file descriptors and namespace identifiers. strace consumes these ioctl numbers, fixed inode/id constants, request structs, and namespace type masks to decode nsfs operations such as `NS_GET_USERNS`, `NS_GET_PARENT`, mount namespace iteration, pid translation between pid namespaces, and namespace identity queries.

## Important APIs, Types, and Dependencies

The header depends on `linux/ioctl.h` for `_IO`/`_IOR` encodings and `linux/types.h` for fixed-width ABI types. Important exports include `NSIO`, `NS_GET_USERNS`, `NS_GET_PARENT`, `NS_GET_NSTYPE`, `NS_GET_OWNER_UID`, `NS_GET_PID_FROM_PIDNS`, `NS_GET_TGID_FROM_PIDNS`, `NS_GET_PID_IN_PIDNS`, `NS_GET_TGID_IN_PIDNS`, `NS_GET_MNTNS_ID`, `NS_GET_ID`, and the mount namespace ioctls `NS_MNT_GET_INFO`, `NS_MNT_GET_NEXT`, and `NS_MNT_GET_PREV`. `struct mnt_ns_info`, `struct nsfs_file_handle`, and `struct ns_id_req` are explicitly versioned by size macros. `enum init_ns_ino`, `enum init_ns_id`, and `enum ns_type` expose stable namespace identity constants.

## Control Flow, State, and Integration

There is no executable control flow. The ABI describes request/response layout for kernel ioctl handlers on namespace file descriptors and for newer namespace listing/stat APIs. State is external kernel namespace state: namespace ids, inodes, owning user namespace ids, mount counts, and pid translations. The strace integration point is decoding ioctl command numbers and nested fields without interpreting them as process-local state.

## Risks and Test Signals

Risks are ABI-size drift, confusing namespace inode constants with namespace ids, and treating `enum ns_type` as arbitrary bit flags rather than clone-style namespace type values. Test signals include strace decoding every nsfs ioctl name, printing `struct mnt_ns_info` and `struct ns_id_req` fields with correct widths, and preserving unknown future structure tail bytes by honoring the `size` field.
