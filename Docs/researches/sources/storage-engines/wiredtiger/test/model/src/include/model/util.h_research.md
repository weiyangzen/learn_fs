# sources/storage-engines/wiredtiger/test/model/src/include/model/util.h

Purpose: declares common RAII guards, configuration parsing, shared memory support, string/path helpers, and WT cursor/utility adapters used by the model and tests.

Important APIs and types: guards `wiredtiger_connection_guard`, `wiredtiger_cursor_guard`, `wiredtiger_session_guard`, and `kv_transaction_guard`; `config_map` with parsing, merge, typed getters, and keys; `shared_memory`; `at_cleanup`; string/path helpers `decode_utf8`, `directory_path`, `executable_path`, `model_library_path`, `ends_with`, `starts_with`, `parse_uint64`, `join`, `quote`; WT cursor helpers `wt_cursor_insert/remove/search/truncate/update`; build/disagg/table helpers `wt_build_dir_path`, `wt_disagg_config_string`, `wt_disagg_pick_up_latest_checkpoint`, `wt_evict`, `wt_extension_path`, `wt_list_tables`.

Control flow: guards close resources in destructors. `kv_transaction_guard` commits unless the transaction is failed, in which case it rolls back; destructor exceptions are logged to stderr. `config_map::from_string` parses WT-style nested configs into variant values. Cursor helpers set keys/values via `data_value` conversion then call WT APIs.

State and persistence: guards hold raw WT pointers but do not own data beyond closing resources. `shared_memory` owns a named shared-memory block for subprocess/runner communication. `config_map` stores parsed configuration in an unordered map.

Dependencies and integration: includes `core.h`, `data_value.h`, `kv_transaction.h`, and `wiredtiger.h`. Used throughout debug parsing, runners, generator config parsing, test utilities, and verification.

Risks: destructors swallow or log close/commit errors, which can hide cleanup failures. `config_map` typed getters throw `std::bad_variant_access` or runtime errors on bad keys/types. Shared memory lifetime depends on implementation cleanup. Cursor helpers assume cursor formats match `data_value` content.

Test signals: tests should cover config parser nesting/arrays/merge, RAII close paths, transaction guard commit/rollback, quote/decode parsing, path helpers, table listing, disaggregated config helpers, and WT cursor adapters through model/WT comparison tests.
