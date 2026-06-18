# File Research: sources/os/linux/linux/fs/devpts/Makefile

## Role

Build definition for the Linux `/dev/pts` virtual filesystem.

## Behavior

- Builds `devpts.o` when `CONFIG_UNIX98_PTYS` is enabled.
- Composes the devpts object from `inode.o`.

## Research Notes

The makefile confirms that the devpts implementation in this group is contained in `fs/devpts/inode.c`.
