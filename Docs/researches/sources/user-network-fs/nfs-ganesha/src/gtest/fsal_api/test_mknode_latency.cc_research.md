<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/gtest/fsal_api/test_mknode_latency.cc -->
## sources/user-network-fs/nfs-ganesha/src/gtest/fsal_api/test_mknode_latency.cc

Purpose: benchmarks special-node creation using `mknode` and `fsal_create(..., SOCKET_FILE, ...)`.

Important APIs/types/functions: tests call `obj_ops->mknode`, `fsal_create`, `lookup`, `fsal_remove`, `nfs_export_get_root_entry`, and `mdcdb_get_sub_handle`. Full fixture creates/removes 100000 regular files before measuring.

Control flow/state: simple tests create a socket node, verify lookup, release handles, and remove it. Loop tests create one million socket nodes and remove them. Full and bypass variants measure in populated directories and backend-root paths.

Dependencies/integration: requires backend support for `SOCKET_FILE` nodes; many network/object filesystems may not support this operation. Uses embedded Ganesha and MDCACHE bypass hooks.

Risks: bypass tests overwrite `sub_hdl` with `nfs_export_get_root_entry(a_export, &sub_hdl)` after obtaining an MDCACHE sub-handle, which deserves scrutiny for intent and reference ownership. Special node creation may require privileges or be unsupported, causing backend-specific failures.

Test signals: zero status for mknode/create/remove, lookup identity in simple cases, and average timing output for object-op, wrapper, full-directory, and bypass variants.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/gtest/fsal_api/test_mknode_latency.cc -->
