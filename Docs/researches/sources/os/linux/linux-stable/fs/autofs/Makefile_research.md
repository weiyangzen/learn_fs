# File Research: sources/os/linux/linux-stable/fs/autofs/Makefile

## Purpose
Builds the autofs filesystem object when `CONFIG_AUTOFS_FS` is enabled.

## Main Contents
Defines `autofs4.o` as the module/built-in target and composes it from `init.o`, `inode.o`, `root.o`, `symlink.o`, `waitq.o`, `expire.o`, and `dev-ioctl.o`.

## Risks / Review Notes
The object name remains `autofs4.o` for historical reasons while the module and filesystem are presented as autofs. Any new source file must be added here to be included in the driver.
