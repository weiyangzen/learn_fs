# File Research: sources/local-fs/reiserfsprogs/resize_reiserfs/fe.c

Kernel online-resize frontend for `resize_reiserfs`.

Major responsibilities:
- `resize_fs_online()` finds the mount entry for a device.
- Constructs a `resize=<blocks>` remount option.
- Calls `mount(..., MS_REMOUNT, buf)` to ask the kernel ReiserFS driver to resize the mounted filesystem.

Dependencies and interactions:
- Uses `misc_mntent()` to map device to mount table entry.
- Uses Linux mount flags and libc `mount()`.
- Called by `resize_reiserfs.c` when the target filesystem is mounted and the change is an online resize.

Risks and notes:
- `buf` is 40 bytes and populated with `sprintf`; this is likely enough for signed 64-bit decimal plus prefix, but not bounds-checked.
- Failure paths abort through `die()`.
