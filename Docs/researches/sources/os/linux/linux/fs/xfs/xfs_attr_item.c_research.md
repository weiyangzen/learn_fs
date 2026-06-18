# File Research: sources/os/linux/linux/fs/xfs/xfs_attr_item.c

Implements logged deferred extended attribute intent/done items: ATTRI and ATTRD, including normal transaction logging, relogging, cancellation, and log recovery.

Key elements:
- Defines ATTRI/ATTRD slab caches and log item ops.
- `xfs_attri_log_nameval` stores refcounted shared name/new-name/value/new-value buffers for deferred attr operations.
- ATTRI lifecycle functions allocate, format, size, unpin, release, match, and free intent items.
- ATTRD lifecycle functions allocate, format, release, and link done items to their ATTRI.
- `xfs_attr_log_item` fills `xfs_attri_log_format` from `xfs_attr_intent`, with special fields for parent pointer operations.
- `xfs_attr_create_intent` creates a logged ATTRI only for `XFS_DA_OP_LOGGED` operations and shares the name/value buffer with deferred work.
- `xfs_attr_finish_item` resumes the state-machine attr operation via `xfs_attr_set_iter`, returning `-EAGAIN` until the delayed attr operation reaches `XFS_DAS_DONE`.
- `xfs_attri_validate` validates recovered intent fields against feature flags, namespace bits, name lengths, value sizes, parent pointer requirements, and inode numbers.
- `xfs_attri_recover_work` reconstructs `xfs_attr_intent` and `xfs_da_args` from recovered log data, igets the target inode, reads attr extents when needed, initializes add/replace/remove state, and queues recovered deferred work.
- `xfs_attr_recover_work` validates recovered buffers, creates a recovery transaction, finishes the recovered intent, and captures/commits deferred operations.
- `xfs_attr_relog_intent` copies an intent into a new ATTRI to push the log tail forward.
- `xfs_attr_defer_add` converts high-level set/replace/remove and parent-pointer operations into logged op flags and queues the deferred item.
- `xlog_recover_attri_commit_pass2` parses and validates recovered ATTRI log vectors, reconstructs shared name/value buffers, creates an incore ATTRI, and registers it with intent recovery.
- `xlog_recover_attrd_commit_pass2` releases matching recovered ATTRIs when a done item is found.

Dependencies:
- Uses XFS defer ops framework, xattr state machine, parent pointer validation, log recovery, transaction reservation, and inode recovery iget paths.
- Shares operation definitions with `xfs_log_format.h` and `xfs_attr_item.h`.

Research notes:
- ATTRI supports regular logged xattrs and parent pointer set/remove/replace operations; validation is feature-gated.
- Name/value buffers can exceed 64 KiB, so allocation uses `xlog_kvmalloc`.
- Parent pointer operations record inode generation and validate parent record values during recovery.
- Recovery treats malformed intent vectors as metadata corruption and rejects the entire intent.
- ATTRI reference counting accounts for races between AIL insertion and ATTRD processing.
