# sources/test-tools/stress-ng/core-setting.c

Purpose: stores parsed stress-ng settings in a linked list, supports per-current-stressor lookup with global fallback, and provides sorted debug/user display.

Important APIs/types/functions: `stress_setting_free`, `stress_setting_show`, `stress_setting_dbg`, `stress_setting_set`, `stress_setting_global_set`, `stress_setting_get`, `stress_setting_set_true`, and `stress_setting_global_set_true`. `stress_setting_generic_set` is the central insert/update routine.

Control flow: setting writes validate non-null name/value, search for an existing `(stressor_name,name)` pair, allocate if missing, store `g_item_current`, mark globals by stressor name, and copy the typed value into a union. Strings are duplicated and previous string storage is freed on update. `stress_setting_get` walks from `setting_head`, starts paying attention once it reaches `g_item_current`, stops after leaving the current item unless the setting is global, and writes the requested value according to stored type. Percent-of-filesystem types are converted at lookup time using `stress_fs_size_get`. Display functions collect matching settings into arrays, sort by name with `shim_qsort`, and print formatted values.

State and persistence: private process-global `setting_head`/`setting_tail` own all settings until `stress_setting_free`. Values persist across stressor setup and child application within the process.

Dependencies/integration: relies on `g_item_current`, `g_opt_flags`, `stress_const_optdup`, size-format helpers, filesystem size helpers, logging functions, and the sort shim.

Risks: lookup behavior depends on insertion order and `g_item_current`; misordered settings can shadow or hide values. Error handling exits the process on programmer errors or allocation failure. There is no synchronization for concurrent mutation.

Test signals: set/get every `stress_type_id_t`, update string settings, global versus per-stressor precedence, percent conversion, sorted display, and freeing after repeated updates.
