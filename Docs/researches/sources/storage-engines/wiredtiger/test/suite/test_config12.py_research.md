<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_config12.py -->
# sources/storage-engines/wiredtiger/test/suite/test_config12.py

Purpose: tests verbose configuration validation warnings emitted under `debug_mode=(configuration=true)`.

Important APIs and control flow: `expect_verbose()` is a context manager that clears stdout, opens a connection with a config, yields it, reads stdout, splits verbose messages, and regex-matches each line against expected patterns. Tests verify default warnings, dirty target over target, dirty trigger over trigger, and updates trigger over eviction trigger, with parallel checks that `debug_mode=(configuration=false)` emits no warnings.

State, persistence, and dependencies: state is mostly stdout capture and transient connection handles; the test does not need durable data. Dependencies include regex matching, `wttest` stdout helpers, connection open/close, and configuration normalization/warning logic.

Integration points: validates diagnostic behavior, not just config acceptance. It covers automatic adjustment warnings for eviction-related settings.

Risks and test signals: warning text changes can break regexes; output truncation is handled by dropping a partial last line. Pass signals are warnings only when debug configuration validation is enabled and each message matching an expected category.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_config12.py -->
