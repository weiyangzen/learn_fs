# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/instance.c

## Role

`instance.c` implements illumos device instance-number assignment. It maintains the in-kernel representation of persistent `/etc/path_to_inst` mappings from device tree paths and driver binding names to stable instance numbers.

## Main Behavior

The core state is `e_ddi_inst_state`, containing an instance tree rooted at `ins_root`, a list of driver entries without known majors, a dirty flag, and a reentrant global serialization lock.

`e_ddi_instance_init()` initializes the tree, optionally calls platform I/O alias setup, reads `INSTANCE_FILE` or its backup, and falls back to rebuild/preassignment when the file is missing, empty, or marked with the bootstrap magic string. Rebuilds force reconfiguration boot behavior so `/dev` and `path_to_inst` are regenerated together.

Instance tree nodes are `in_node_t` path components with unit addresses. Driver bindings are `in_drv_t` entries attached to nodes. Driver entries move through provisional, permanent, and borrowed states around `e_ddi_assign_instance()`, `e_ddi_keep_instance()`, and `e_ddi_free_instance()`.

## Instance Assignment

`e_ddi_assign_instance()` first allows platform override, then bypasses the persistent tree for pseudo devices. For normal devices it walks or creates the path node, handles aliases through `e_ddi_borrow_instance()`, allocates a driver entry when needed, assigns an instance using either preassigned `devi_instance` or `in_next_instance()`, and hashes the result onto the corresponding `devnames` major list.

`in_assign_instance_block()` supports driver.conf-controlled contiguous instance blocks for multi-port NICs and similar devices. It reads `ddi-instance-blocks`, matches the current device path against configured suffixes, allocates a contiguous block with `in_next_instance_block()`, and inserts persistent mappings for all paths in the block, including devices not currently present.

`in_next_instance_block()` depends on sorted `dn_inlist` entries. It can allocate quickly from `dn_instance`, or search for holes while respecting the preassigned boundary `dn_pinstance`.

## Persistence And Walking

`in_pathin()` parses entries from `path_to_inst`, normalizes binding names, rejects duplicate path/driver mappings and duplicate instance numbers, and creates permanent tree entries.

`e_ddi_walk_instances()` walks permanent mappings and reconstructs full paths with `in_walk_instances()`. `e_ddi_instance_majorinstance_to_path()` performs the reverse lookup from major and instance to a path.

Dirty state is tracked with `ins_dirty`; changes post a devfs sysevent through `i_log_devfs_instance_mod()` so userland can synchronize instance data.

## Locking And Invariants

All instance-tree mutation is serialized by `e_ddi_enter_instance()` / `e_ddi_exit_instance()`, which support recursive entry by the owning thread. Many helpers assert `ins_busy`.

Important invariants:
- Parents are instantiated before children and destroyed after them.
- Driver entries are removed before their owning nodes.
- `dev_info_t` and `in_node_t` back-pointers must agree while linked.
- `dn_inlist` is sorted by instance number.
- Newly introduced holes force `dn_instance = IN_SEARCHME`.

## Dependencies

This file depends on DDI device tree state, `devnamesp`, driver major lookup, binding-name aliasing, platform instance overrides, sysevents, boot flags, and cluster upgrade compatibility.

## Research Notes

This is a persistence and boot-enumeration file rather than a filesystem file, but it directly affects stable `/dev` naming. Audit-sensitive areas are alias borrow/return behavior, contiguous block assignment, preassigned instance boundary handling, duplicate suppression during `path_to_inst` parsing, and dirty/sysevent synchronization.
