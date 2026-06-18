## sources/storage-engines/wiredtiger/src/utilities/util_load.h

Purpose: shared header for classic and JSON load implementations. It declares the config-list container, load config manipulation helpers, JSON load flags, and `util_load_json`.

Important APIs/types/functions: `CONFIG_LIST` stores a NULL-terminated array of alternating URI/config strings with entry and allocation counts. Functions declared here include `config_exec`, `config_list_add`, `config_list_free`, `config_reorder`, `config_update`, and `util_load_json`. Flags are `LOAD_JSON_APPEND` and `LOAD_JSON_NO_OVERWRITE`.

Control flow: no executable code, but it defines the shared interface allowing `util_load_json.c` to reuse classic load metadata creation and config override logic before inserting JSON records.

State and persistence behavior: `CONFIG_LIST` owns heap strings that eventually drive persistent schema creation. JSON flags map CLI behavior to cursor config (`append`, `overwrite=false`) in the JSON loader.

Dependencies and integration points: included by `util_load.c` and `util_load_json.c`, and indirectly tied to dump/load format compatibility. Flag generation comments indicate values are maintained by an automatic flag-value process.

Risks: callers must maintain alternating URI/config order and NULL termination or `config_exec`/update loops will walk invalid memory. Adding flags requires preserving generated value conventions. Since JSON and classic load share helpers, changes in config update behavior affect both formats.

Test signals: compile-time coverage by both loaders, config-list growth/free tests through large metadata inputs, JSON append/no-overwrite behavior, and classic/JSON round-trip tests that exercise shared reorder/update/create helpers.
