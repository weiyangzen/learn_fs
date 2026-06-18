# File Research: sources/os/linux/linux/fs/configfs/item.c

## Purpose
Provides public helper routines for initializing, naming, reference-counting, cleaning up, and searching configfs items and groups.

## Main Elements
- Initialization: `config_item_init()`, `config_item_init_type_name()`, `config_group_init_type_name()`, and `config_group_init()`.
- Naming: `config_item_set_name()` stores short names in `ci_namebuf` and allocates longer names dynamically.
- References: `config_item_get()`, `config_item_get_unless_zero()`, and `config_item_put()` wrap `kref`.
- Cleanup: `config_item_cleanup()` frees dynamic names, calls item release callbacks, and drops group/parent references.
- Lookup: `config_group_find_item()` searches a group's `cg_children` by name and returns a referenced item.

## Dependencies And Integration
These helpers are exported to configfs clients and are used internally by `dir.c` to maintain hierarchy references. Cleanup callbacks come from `config_item_type`.

## Risk Notes
Name storage must avoid leaking old dynamic names on rename. Reference ownership is shared between parent links, child lists, and client callbacks; a missing put or double put would corrupt configfs object lifetime.
