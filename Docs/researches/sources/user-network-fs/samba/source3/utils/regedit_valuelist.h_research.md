# sources/user-network-fs/samba/source3/utils/regedit_valuelist.h

`regedit_valuelist.h` declares the value-list model and UI surface for regedit. `struct value_item` stores registry value type, raw `DATA_BLOB`, value name, rendered data string, and an `unprintable` flag. `struct value_list` stores ncurses windows, panel, value count, value array, and the backing `multilist`.

The API covers allocation, show/resize/selection, full load, quick load, sync, current item get/set, set by name, cursor driving, and forward/backward search through a `regedit_search_match_fn_t`.

State is an in-memory snapshot of one registry key's values. The public struct layout allows direct inspection of `nvalues` and `values`, but callers must preserve row-pointer stability for the multilist. Dependencies include ncurses, panel, Samba `DATA_BLOB`, generic `registry_key`, and regedit search declarations.

Risks include tight coupling through public fields and a stale-looking declaration for `value_list_load_names`, which is not implemented in the paired source in this subset. Test signals: build/link checks for declared symbols, load/sync of value arrays, cursor movement, current item by name, and search matches over stable `value_item` pointers.
