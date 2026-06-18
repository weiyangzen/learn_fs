# sources/storage-engines/wiredtiger/test/model/src/core/util.cpp

Purpose: shared utilities for configuration parsing, RAII-adjacent support, shared memory, UTF-8 byte recovery, path discovery, disaggregated storage helpers, eviction, extension lookup, and table listing.

Important APIs and functions: `config_map::from_string/parse_array/merge` parse WiredTiger-like config strings into nested maps/arrays. `shared_memory` wraps POSIX `shm_open`, `ftruncate`, `mmap`, immediate unlink, and `munmap`. `decode_utf8` uses iconv to convert JSON Unicode escapes back to byte values from `wt printlog -u`. Path helpers find directory/executable/model library/build directory. `wt_disagg_config_string` builds palite precise-checkpoint config. `wt_disagg_pick_up_latest_checkpoint` queries page-log checkpoint metadata and reconfigures WiredTiger. `wt_evict` opens a debug eviction cursor. `wt_list_tables` scans metadata.

Control flow and state: config parsing is hand-written and preserves nested values as variants. Shared memory is process-shared and zero-initialized. Disagg checkpoint pickup opens sessions/page logs and uses guards for cleanup.

Dependencies and integration: uses POSIX APIs, iconv, dladdr/dirname/readlink, WiredTiger public/internal APIs, and model data conversion helpers. Used by debug-log parser and WT workload runner.

Risks and test signals: parser is narrower than full WiredTiger config grammar. `executable_path` checks `readlink` incorrectly for zero rather than negative and does not NUL-terminate, although typical use may tolerate this. Disagg helpers are platform/build-layout sensitive. Failures surface in model tools, log replay, and disaggregated workload execution.
