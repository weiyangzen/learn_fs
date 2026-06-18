# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/zimage2.c

Small helper for Level 2/DPS image extensions that have no explicit source data. It exports `process_non_source_image`, used by other modules such as `zdps.c` and `zdpnext.c`.

The function calls `gs_image_begin_typed` on the supplied image descriptor and current graphics state, but does not allocate interpreter data-source continuations because no data is passed. The source comment notes the `uses_color` argument is currently hard-coded false and marked wrong, so callers depend on the narrow non-source-image use case.
