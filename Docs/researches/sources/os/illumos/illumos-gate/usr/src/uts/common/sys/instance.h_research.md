# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/instance.h

This header defines device instance-number assignment data structures and APIs around `/etc/path_to_inst`.

Key definitions:
- Instance file paths: `INSTANCE_FILE`, `INSTANCE_FILE_SUFFIX`.
- Kernel/kmemuser structures:
  - `in_node_t` represents the fully populated instance tree parallel to the dev_info tree.
  - `in_drv_t` represents a driver binding/instance entry under an instance node.
- Instance states: `IN_PROVISIONAL`, `IN_PERMANENT`, `IN_UNKNOWN`, `IN_BORROWED`.
- `PTI_GUARD` guard text for `path_to_inst`.
- `IN_SEARCHME` special instance value.

Kernel APIs:
- Initialize/assign/keep/free instances.
- Major+instance to path conversion.
- Clean/orphan handling and enter/exit locking.
- Root access and dirty/clean state.
- Platform override hooks: `impl_assign_instance`, `impl_keep_instance`, `impl_free_instance`.
- Instance tree walking and DDI-MP borrow/return helpers.
- Walk callback return values: continue/terminate.

User API:
- `inst_sync(char *pathname, int flags)` when not `_KERNEL`.
- Sync flags: `INST_SYNC_IF_REQUIRED`, `INST_SYNC_ALWAYS`.

Relevance:
- Device instance stability is fundamental for disk, controller, network, and storage device naming.
