# File Research: sources/os/linux/linux/fs/ocfs2/dlmfs/Makefile

## Purpose
Builds the OCFS2 userspace DLM filesystem module objects when `CONFIG_OCFS2_FS` is enabled.

## Contents
- Adds `ocfs2_dlmfs.o` to the build through `obj-$(CONFIG_OCFS2_FS)`.
- Defines `ocfs2_dlmfs-objs := userdlm.o dlmfs.o`.

## Dependency Meaning
The dlmfs module is composed of:
- `dlmfs.o`: VFS filesystem layer.
- `userdlm.o`: userspace lock-resource DLM protocol layer.
