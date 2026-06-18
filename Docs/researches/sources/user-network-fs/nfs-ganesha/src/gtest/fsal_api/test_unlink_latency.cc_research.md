# sources/user-network-fs/nfs-ganesha/src/gtest/fsal_api/test_unlink_latency.cc

## Purpose
This executable measures file removal/unlink latency using direct object operations, `fsal_remove`, and MDCACHE bypass handles. It creates hard links to one file so the benchmark can remove many directory entries without creating separate file contents.

## Important APIs, Types, And Functions
Tests use `fsal_create`, `obj_ops->open2`, `obj_ops->close`, `obj_ops->link`, `obj_ops->unlink`, `obj_ops->lookup`, `fsal_remove`, and `mdcdb_get_sub_handle`. `gtws_subcall` temporarily switches `op_ctx->fsal_export` to the sub-export for bypass `open2`.

## Control Flow, State, And Persistence
Simple tests create one file, unlink it, then assert lookup returns `ERR_FSAL_NOENT`. `FSALREMOVE` and full tests create a base file and one million hard links named `fl-%08x`; timing encloses removal of those links only. Full bypass creates links and removes them through sub-root/sub-object handles. After the benchmark, the original base file is removed and its handle reference is released.

## Dependencies And Integration Points
The file depends on hard-link support, FSAL lookup/no-entry semantics, sub-export context switching, and the base fixture's large-directory priming for full tests. It directly exercises link/unlink interaction and wrapper removal semantics.

## Risks And Test Signals
The million-link setup can exceed backend link-count or directory scalability limits and may be expensive to clean up on early assertion failure. The bypass simple test uses lower-level `close` rather than `close2`, matching the direct sub-handle open path. Signals include no-entry lookup after simple unlink, status checks for every link and remove, and successful final cleanup.
