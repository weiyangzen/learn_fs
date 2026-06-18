<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_strerror01.py -->
# sources/storage-engines/wiredtiger/test/suite/test_strerror01.py

Purpose: verifies the Python session `strerror` API returns expected strings for WiredTiger sub-level error codes.

Important APIs/types/functions: `test_strerror` extends `WiredTigerTestCase` and `suite_subprocess`; it uses constants such as `WT_NONE`, `WT_BACKGROUND_COMPACT_ALREADY_RUNNING`, `WT_CACHE_OVERFLOW`, multiple conflict codes, and `session.strerror`.

Control flow: iterate the `sub_errors` list of `(code, expected_string)` pairs and call `check_error_code`, which asserts `self.session.strerror(error) == expected`.

State and persistence behavior: no persistent state is involved; this is a binding/API mapping test.

Dependencies/integration points: covers Python exposure of C error-code constants, string formatting, and session API behavior. Risks are exact string coupling and new/renamed codes; the signal is equality for every listed code, including live restore and disaggregated-storage conflict codes.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_strerror01.py -->
