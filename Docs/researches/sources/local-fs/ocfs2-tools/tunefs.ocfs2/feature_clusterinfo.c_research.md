# File Research: sources/local-fs/ocfs2-tools/tunefs.ocfs2/feature_clusterinfo.c

## Purpose
Toggles the clusterinfo incompat feature and synchronizes cluster descriptor metadata.

## Main Behavior
- `enable_clusterinfo()`:
  - No-ops if feature is already set.
  - Prompts.
  - Sets `OCFS2_FEATURE_INCOMPAT_CLUSTERINFO`.
  - Clears `OCFS2_FEATURE_INCOMPAT_USERSPACE_STACK` because clusterinfo supersedes it.
  - Reads the running cluster descriptor and writes it to disk via `ocfs2_set_cluster_desc()`.
- `disable_clusterinfo()`:
  - No-ops if feature is absent.
  - Prompts.
  - If the superblock still indicates a userspace stack, re-sets `USERSPACE_STACK`.
  - Clears `CLUSTERINFO` and writes the superblock.
- Defines `clusterinfo_feature` with `TUNEFS_FLAG_RW`.

## Dependencies
- O2CB cluster descriptor APIs.
- OCFS2 cluster stack feature helpers.
- Tunefs progress and signal wrappers.
