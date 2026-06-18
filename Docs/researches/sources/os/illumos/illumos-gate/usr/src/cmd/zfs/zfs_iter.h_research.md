# File Research: sources/os/illumos/illumos-gate/usr/src/cmd/zfs/zfs_iter.h

Small private header for the `zfs` command's dataset iteration helpers.

Exports:
- `zfs_sort_column_t`, a linked list node describing one sort key.
- `zfs_for_each()`, the central sorted dataset iteration wrapper.
- `zfs_add_sort_column()`, `zfs_free_sort_columns()`, and `zfs_sort_only_by_name()`.

Iteration flags:
- `ZFS_ITER_RECURSE`: recurse through descendants.
- `ZFS_ITER_ARGS_CAN_BE_PATHS`: resolve command arguments as paths as well as dataset names.
- `ZFS_ITER_PROP_LISTSNAPS`: include snapshots according to the pool `listsnapshots` property.
- `ZFS_ITER_DEPTH_LIMIT`: enforce the supplied maximum recursion depth.
- `ZFS_ITER_RECVD_PROPS`: retain/expand received property values.
- `ZFS_ITER_SIMPLE`: use simple snapshot iteration where supported.
- `ZFS_ITER_LITERAL_PROPS`: use literal/parsable property values.

Integration role:
- Included by `zfs_main.c` for list/get/set-like command walking.
- Implemented by `zfs_iter.c`.
- Uses libzfs types such as `zfs_prop_t`, `zfs_type_t`, `zprop_list_t`, and `zfs_iter_f`, supplied by included libzfs headers in the including translation unit.

Risk notes:
- Flag semantics are tightly coupled to `zfs_iter.c`; adding a flag requires updating recursion, property expansion, or open behavior there.
- `zfs_sort_column_t.sc_last` is used only on the head node to append efficiently; callers should treat the list as opaque.
