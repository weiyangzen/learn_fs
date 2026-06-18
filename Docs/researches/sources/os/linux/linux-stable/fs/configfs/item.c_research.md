# File Research: sources/os/linux/linux-stable/fs/configfs/item.c

This file implements generic configfs item and group reference-counting utilities.

Key responsibilities:
- Initializes config items and groups.
- Sets item names using either the fixed `ci_namebuf` or dynamically allocated storage.
- Exports get/put helpers for config items.
- Cleans up items on final reference drop.
- Searches child items in a config group.

Important control flow:
- `config_item_set_name()` first tries `ci_namebuf`, then uses `kvasprintf()` if the formatted name is too long.
- `config_item_cleanup()` frees dynamic names, calls the item type’s `release()` callback, and drops group/parent references.
- `config_group_find_item()` scans `cg_children` under the caller-held subsystem mutex and returns a referenced item on match.

Dependencies:
- Used by configfs directory lifecycle and by configfs clients.
- Public exports form part of the configfs API.

Risks and invariants:
- `config_item_put()` is the only final-release path and delegates to kref.
- If a type provides `release()`, it is responsible for object-specific cleanup after generic cleanup steps.
- Group child lists require external locking by `cg_subsys->su_mutex`.
