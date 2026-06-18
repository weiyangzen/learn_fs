# File Research: sources/local-fs/ocfs2-tools/tunefs.ocfs2/feature_local.c

## Purpose
Switches an OCFS2 filesystem between local single-node mode and cluster-aware mode.

## Main Behavior
- `enable_local()`:
  - No-ops if already local.
  - Prompts.
  - Sets `OCFS2_FEATURE_INCOMPAT_LOCAL_MOUNT`.
  - Clears `OCFS2_FEATURE_INCOMPAT_USERSPACE_STACK`.
  - Writes superblock.
- `disable_local()`:
  - No-ops if already cluster-aware.
  - Prompts.
  - Initializes O2CB because local filesystems are not connected during `tunefs_open()`.
  - Reads the running cluster descriptor.
  - Clears local mount bit.
  - Writes the cluster descriptor to disk with `ocfs2_set_cluster_desc()`.

## Dependencies
- O2CB running cluster discovery.
- OCFS2 local mount and cluster descriptor helpers.
- Tunefs progress and signal wrappers.

## Notes
`disable_local()` contains two consecutive `tunefs_block_signals()` calls around `ocfs2_set_cluster_desc()` where the second likely intended to unblock. That affects signal-block nesting but later process cleanup may still finish normally.
