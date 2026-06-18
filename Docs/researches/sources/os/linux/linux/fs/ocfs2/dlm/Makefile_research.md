# File Research: sources/os/linux/linux/fs/ocfs2/dlm/Makefile

## Purpose
Builds the OCFS2 O2CB distributed lock manager object when `CONFIG_OCFS2_FS_O2CB` is enabled.

## Build Output
Adds `ocfs2_dlm.o` to the build:
```make
obj-$(CONFIG_OCFS2_FS_O2CB) += ocfs2_dlm.o
```

## Component Objects
`ocfs2_dlm.o` is linked from:
- `dlmdomain.o`
- `dlmdebug.o`
- `dlmthread.o`
- `dlmrecovery.o`
- `dlmmaster.o`
- `dlmast.o`
- `dlmconvert.o`
- `dlmlock.o`
- `dlmunlock.o`

This places `dlmast.c` in the main DLM module with domain, recovery, mastership, conversion, lock, and unlock code.
