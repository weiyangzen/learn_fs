# File Research: sources/os/linux/linux-stable/fs/ocfs2/dlm/Makefile

## Summary
Builds the OCFS2 in-kernel DLM object when `CONFIG_OCFS2_FS_O2CB` is enabled.

## Main Responsibilities
- Add `ocfs2_dlm.o` to the build for the O2CB-backed OCFS2 filesystem configuration.
- Define the composite object members that are linked into `ocfs2_dlm.o`.

## Key Interfaces
- `obj-$(CONFIG_OCFS2_FS_O2CB) += ocfs2_dlm.o` gates the module/object on the O2CB OCFS2 configuration.
- `ocfs2_dlm-objs` lists `dlmdomain.o`, `dlmdebug.o`, `dlmthread.o`, `dlmrecovery.o`, `dlmmaster.o`, `dlmast.o`, `dlmconvert.o`, `dlmlock.o`, and `dlmunlock.o`.

## Important Behavior
The DLM is compiled as one composite object from domain management, debug support, worker/recovery threads, mastership, AST/BAST delivery, conversion, lock, and unlock implementation files.

## State and Synchronization
The Makefile has no runtime state. Its ordering only expresses build composition, not initialization order.

## Cross-File Interactions
The listed objects implement the interfaces declared in `dlmapi.h` and `dlmcommon.h`. `dlmast.c` is one member of this composite object.

## Risks
Configuration gating is important: without `CONFIG_OCFS2_FS_O2CB`, the in-kernel O2CB DLM object is not built. Adding DLM source files requires updating this object list or the code will not be linked.
