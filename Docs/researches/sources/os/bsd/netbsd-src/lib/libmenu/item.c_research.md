# File Research: sources/os/bsd/netbsd-src/lib/libmenu/item.c

Implements item-level libmenu APIs and default item state. It supports visibility/name/description accessors, item hooks, selected-item enumeration, selectable-option management, value setting, allocation/freeing, current-item selection, and item index lookup.

Important dependencies: `<menu.h>`, `<stdlib.h>`, `<string.h>`, and `internals.h`.

Key behavior: `new_item()` deep-copies name and optional description; `free_item()` refuses connected items; `set_item_value()` requires a connected item and denies changes under `O_ONEVALUE`; `item_selected()` allocates an array of selected indexes for the caller. Notable edge: `set_current_item()` only checks the item index, not that `item->parent` is the target menu.
