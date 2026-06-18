# File Research: sources/os/linux/linux-stable/fs/devpts/Makefile

## Purpose

Builds the `/dev/pts` virtual filesystem when Unix98 PTYs are enabled.

## Main Responsibilities

- Adds `devpts.o` to the build under `CONFIG_UNIX98_PTYS`.
- Defines `devpts-y` as `inode.o`.

## Dependencies

- Controlled by `CONFIG_UNIX98_PTYS`.
- The compiled filesystem logic lives in `fs/devpts/inode.c`.
