# File Research: sources/local-fs/ocfs2-tools/tunefs.ocfs2/libocfs2ne.h

## Purpose
Public header for the `tunefs.ocfs2` helper library and feature/operation plugin framework.

## Main Content
- Defines open flags:
  - `TUNEFS_FLAG_RO`
  - `TUNEFS_FLAG_RW`
  - `TUNEFS_FLAG_ONLINE`
  - `TUNEFS_FLAG_NOCLUSTER`
  - `TUNEFS_FLAG_ALLOCATION`
  - `TUNEFS_FLAG_SKIPCLUSTER`
  - `TUNEFS_FLAG_LARGECACHE`
- Defines `enum tunefs_feature_action`.
- Defines `struct tunefs_feature`, including feature name, feature bits, open flags, enable/disable callbacks, and selected action.
- Provides `DEFINE_TUNEFS_FEATURE_COMPAT`, `DEFINE_TUNEFS_FEATURE_RO_COMPAT`, and `DEFINE_TUNEFS_FEATURE_INCOMPAT`.
- Defines `struct tunefs_operation` and `DEFINE_TUNEFS_OP`.
- Declares shared helpers for initialization, signal blocking, in-progress bits, number parsing, journal sizing, free-space lookup, zeroing clusters, online ioctl, DLM locks, inode scanning, open/close, operation/feature dispatch, and debug main functions.
- Defines `struct tunefs_trailer_context` and declares directory trailer helpers.

## Design Notes
The header documents expected behavior for feature and operation modules: idempotence, `tools_interact()` before writes, quiet normal operation, and use of shared verbose/error/progress APIs.
