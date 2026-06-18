# File Research: sources/local-fs/ocfs2-tools/include/ocfs2-kernel/ocfs2_ioctl.h

## Purpose

Defines OCFS2 ioctl numbers and the userspace-visible argument structures used for file flags, space reservation, online resize, reflink, filesystem information queries, and extent movement.

## Main Contents

- `OCFS2_IOC_GETFLAGS` / `OCFS2_IOC_SETFLAGS` and 32-bit variants compatible with standard file flag operations.
- `struct ocfs2_space_resv` and XFS-compatible reservation ioctl numbers for reserve/unreserve operations; allocation/free variants are listed but documented as unsupported.
- `struct ocfs2_new_group_input` plus group extend/add ioctl numbers for online resizing.
- `struct reflink_arguments` and `OCFS2_IOC_REFLINK` for clone-style link creation by passing old/new path pointers and preserve flag.
- `struct ocfs2_info` multiplexed request container and typed request payloads for cluster size, block size, max slots, label, UUID, feature flags, journal size, free inode stats, and free fragmentation stats.
- `enum ocfs2_info_type` request codes and request status flags for filled/error/non-coherent responses.
- `struct ocfs2_move_extents` and move/defrag flags for moving file extents, including partial and auto-defrag modes.

## Dependencies and Integration

- Uses OCFS2 constants from `ocfs2_fs.h`, especially UUID, label, and max slot sizes.
- Intended to match kernel ioctl ABI; user tools must preserve structure size and field ordering.

## Research Notes

- The info ioctl is intentionally request-granular for forward/backward compatibility.
- Some request payload arrays scale to `OCFS2_MAX_SLOTS`, making this header tied to the on-disk slot limit.
