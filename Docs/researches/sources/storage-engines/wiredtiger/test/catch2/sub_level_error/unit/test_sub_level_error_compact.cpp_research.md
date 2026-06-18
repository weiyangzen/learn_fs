# Research: sources/storage-engines/wiredtiger/test/catch2/sub_level_error/unit/test_sub_level_error_compact.cpp

## sources/storage-engines/wiredtiger/test/catch2/sub_level_error/unit/test_sub_level_error_compact.cpp

Purpose: Regression tests for sub-level error handling in background compaction configuration paths, especially `__wt_background_compact_signal`.

Important APIs/types: real `WT_SESSION_IMPL`, `WT_CONNECTION_IMPL`, connection flags `WT_CONN_IN_MEMORY` and `WT_CONN_READONLY`, `conn_impl->background_compact.running/config`, and `WT_BACKGROUND_COMPACT_ALREADY_RUNNING`.

Control flow: sections check unsupported in-memory/readonly database returns `ENOTSUP` without changing last-error info; missing `background` config returns `WT_NOTFOUND`; `background=false` and `background=true` succeed; matching an already-running configuration succeeds; and attempting to reconfigure a running background compact with a different config returns `EINVAL` and records the sub-level error plus message.

State and persistence: mutates connection flags and background compact state. The test resets flags/config where needed so connection close remains valid. Error-info persistence is per session.

Dependencies/integration: tied to compaction config parser and connection state. Risks are manual mutation of internal connection fields and ownership of `background_compact.config` strings. Test signals include return codes and `check_error_info`.

<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/sub_level_error/unit/test_sub_level_error_compact.cpp -->
