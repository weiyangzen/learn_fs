# File Research: sources/local-fs/ocfs2-tools/tunefs.ocfs2/Makefile

## Purpose
Builds the `tunefs.ocfs2` implementation, its internal helper library `libocfs2ne.a`, the `o2cluster` utility, man pages, and optional debug executables.

## Main Behavior
- Defines internal libraries:
  - `libtools-internal`
  - `libocfs2`
  - `libo2dlm`
  - `libo2cb`
- Adds conditional `-ldlm_lt` and `-lcmap` based on build support.
- Builds `libocfs2ne.a` from `libocfs2ne.c` and generated `o2ne_err.o`.
- Lists all `OCFS2NE_FEATURES`, including backup super, sparse files, xattr, quota, clusterinfo, append dio, etc.
- Lists `OCFS2NE_OPERATIONS`, such as query, resize, label, journal size, slot count, cluster stack update, and quota sync interval.
- Builds `ocfs2ne`, then hard-links `tunefs.ocfs2` to it.
- Builds `o2cluster` separately.
- Generates `o2ne_err.c` and `o2ne_err.h` from `o2ne_err.et`.
- Supports optional `DEBUG_EXE` binaries for selected operation/feature source files.

## Dependencies
- Project top-level make infrastructure.
- `compile_et` for com_err table generation.
- OCFS2, O2CB, O2DLM, UUID, AIO, com_err, and internal tools libraries.
