# File Research: sources/local-fs/ocfs2-tools/fsck.ocfs2/Makefile

Read coverage: complete file read, 113 lines.

Purpose: builds and installs `fsck.ocfs2` plus its man pages.

Behavior:
- Defines `fsck.ocfs2` as an sbin program.
- Builds from core fsck sources: main driver, directory helpers, extent checking, inode counts, journal replay/checking, passes 0-5, problem prompts, refcount, slot recovery, strings, util, and xattr.
- Links against `libocfs2`, `libo2dlm`, `libo2cb`, `libtools-internal`, com_err, and AIO libraries.
- Adds cluster-stack libraries conditionally for fsdlm/cmap support.
- Uses static linking unless `OCFS2_DYNAMIC_FSCK` is set.
- Generates `prompt-codes.h` by parsing `.SS "CODE"` sections from `fsck.ocfs2.checks.8.in`.
- Provides `check-prompt-dups` to detect duplicate prompt code call sites in the binary.

Risk notes:
- The manual page is part of the build contract: undocumented prompt codes will fail to generate the expected define.
- `prompt-codes.h` is generated in the source directory and cleaned by `o2fsck-clean`.
