# File Research: sources/virtualization/spdk/lib/ftl/utils/ftl_df.h

Defines durable-format object IDs as offsets from a base pointer.

APIs:
- `ftl_df_get_obj_id(base, ptr)` returns byte offset.
- `ftl_df_get_obj_ptr(base, id)` reconstructs pointer.

Used for superblock blob/linked structures and external-buffer mempool references.

Risk:
- Pointer/object bounds are not checked here beyond assertions; callers must validate IDs before conversion when reading durable data.
