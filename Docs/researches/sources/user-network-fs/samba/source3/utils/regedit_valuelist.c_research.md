# sources/user-network-fs/samba/source3/utils/regedit_valuelist.c

`regedit_valuelist.c` implements regedit's registry value table. It loads values from a selected key, sorts them by name, summarizes raw registry data into display strings, supports search navigation, and renders `Name`, `Type`, and `Data` columns through `multilist`.

Public APIs include `value_list_new`, resize/show/selection helpers, `value_list_load_quick`, `value_list_sync`, `value_list_load`, find-next/previous search helpers, current-item setters/getters, and `value_list_driver`. `append_data_summary` formats `REG_DWORD`, string types, `REG_MULTI_SZ`, binary values, and unknown types; unprintable strings are marked and summarized.

The load flow is two-stage. Quick load clears old state, queries value count, enumerates values through `reg_key_get_value_by_index`, and sorts the array. Sync formats data summaries, binds the list data, and refreshes the UI. State is an in-memory snapshot in `struct value_item` arrays; persistence is handled by separate registry mutation code.

Dependencies include generic registry APIs, registry type/data helpers, regedit search matching, ncurses panels, and `regedit_list`. Risks include a one-before-array sentinel in reverse search, potentially huge multi-string summaries, and `isprint` signed-char sensitivity. Test signals: all registry types, unprintable values, empty lists, sorted names, current-item restoration, and search boundaries.
