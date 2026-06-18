# File Research: sources/os/linux/linux/fs/autofs/Makefile

## Summary
Builds the autofs filesystem module.

## Main Contents
- `obj-$(CONFIG_AUTOFS_FS) += autofs4.o`.
- `autofs4-objs := init.o inode.o root.o symlink.o waitq.o expire.o dev-ioctl.o`.

## Important Behavior
The built object name remains `autofs4.o` while the module aliases and filesystem type expose `autofs`.

## Risks
No runtime logic. Build composition must stay in sync with exported symbols across the autofs source files.
