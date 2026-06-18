# File Research: sources/os/linux/linux-stable/fs/ocfs2/move_extents.h

Purpose: declares the OCFS2 move-extents ioctl helper.

Read coverage: complete file read, 12 lines.

Declared APIs:
- `ocfs2_ioctl_move_extents(struct file *filp, void __user *argp)` validates and executes the move-extents ioctl for regular writable OCFS2 files.

Important dependencies:
- Uses Linux `struct file` and userspace pointer annotations; implementation is in `move_extents.c`.

Risk and edge cases:
- All validation and partial-progress copyback semantics live in the implementation; callers should invoke this only from ioctl dispatch with mount write protection expectations.
