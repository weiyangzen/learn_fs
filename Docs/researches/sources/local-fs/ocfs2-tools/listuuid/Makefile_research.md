# File Research: sources/local-fs/ocfs2-tools/listuuid/Makefile

Builds the `listuuid` utility.

Key contents:
- Includes top-level build pre/postamble.
- Links against `libocfs2`, `libo2dlm`, `libo2cb`, `com_err`, `uuid`, and `aio`.
- Adds optional `-ldlm_lt` when fsdlm support is enabled.

Build output:
- Uninstalled program: `listuuid`.

Research notes:
- The Makefile does not include `LIBO2CB_LIBS` in the final `$(LINK)` command despite declaring deps/libs; `listuuid.c` itself mainly uses libocfs2 and OCFS1 compatibility helpers.
