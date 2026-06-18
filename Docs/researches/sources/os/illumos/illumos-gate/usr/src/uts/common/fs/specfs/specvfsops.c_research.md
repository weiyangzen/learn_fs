# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/specfs/specvfsops.c

## Purpose
Provides the loadable filesystem module wrapper and VFS sync operation for `specfs`.

## Key Elements
Registers `specfs` through a `vfsdef_t` whose init function is `specinit` and whose flags include `VSW_ZMOUNT`. `_init` installs the filesystem module, `_info` delegates to `mod_info`, and there is no unload path.

`spec_sync` serializes sync work with `spec_syncbusy`, ignores `SYNC_ATTR`, scans all snodes in the global `stable` table, skips virtual swap vnodes, and collects block-device vnodes with cached data. It holds each vnode before dropping `stable_lock`, then asynchronously writes pages with `VOP_PUTPAGE(..., B_ASYNC, ...)` and releases the hold.

## Dependencies
Depends on specfs globals from `specsubr.c`, including `stable`, `STABLESIZE`, `stable_lock`, `specinit`, and snode/vnode helpers. Uses VFS module registration, vnode cached-data checks, swap-vnode checks, and `VOP_PUTPAGE`.

## Behavior/Risks
The sync path avoids holding `stable_lock` during page writeback by first building a held temporary list through `s_list`. It is intentionally best-effort and returns immediately if another specfs sync is already active. Correct vnode holds are required so snodes do not disappear between the hash scan and asynchronous putpage calls.
