# File Research: sources/os/linux/linux/fs/tracefs/Makefile

Purpose: Builds tracefs core objects.

Build contents:
- `obj-$(CONFIG_TRACING) += tracefs.o`
- `tracefs-objs := inode.o event_inode.o`

Notes:
- tracefs is tied to `CONFIG_TRACING`.
- Main implementation is split between general tracefs inode/mount code and dynamic eventfs inode code.
