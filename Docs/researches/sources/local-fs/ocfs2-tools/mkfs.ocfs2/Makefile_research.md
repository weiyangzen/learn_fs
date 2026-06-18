# File Research: sources/local-fs/ocfs2-tools/mkfs.ocfs2/Makefile

Builds and installs the `mkfs.ocfs2` formatter.

Key contents:
- Installs program under `$(root_sbindir)`.
- Builds from `mkfs.c` and `check.c`.
- Links against `libocfs2`, `libo2dlm`, `libo2cb`, `com_err`, `uuid`, and `aio`.
- Adds optional cluster stack libraries: `-lcmap` and/or `-ldlm_lt`.
- Builds man page `mkfs.ocfs2.8` from `.in` source.

Research notes:
- This target is tightly coupled to OCFS2 cluster libraries because formatting safety checks may query active cluster state and DLM.
