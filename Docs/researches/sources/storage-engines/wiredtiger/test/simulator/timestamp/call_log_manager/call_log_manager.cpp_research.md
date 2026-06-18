# sources/storage-engines/wiredtiger/test/simulator/timestamp/call_log_manager/call_log_manager.cpp

Purpose: command-line replay tool that consumes a WiredTiger API call log in JSON-entry form and drives the in-memory timestamp simulator, asserting simulated return values and queried timestamps match logged expectations.

Important APIs and control flow: the constructor reads the file, strips trailing newlines/commas, wraps entries in `[...]`, parses JSON, obtains the connection singleton, and initializes `_api_map`. Each `call_log_*` method extracts fields from a log entry, normalizes `"(null)"` configs, dispatches to `connection_simulator` or `session_simulator`, asserts the simulator return equals `return.return_val`, and throws on non-zero returns. `process_call_log_entry()` switches on `method_name` for begin/commit/prepare/rollback, session open/close, set/query timestamp, and `timestamp_transaction_uint`.

State and persistence behavior: maintains `_session_map` from logged session IDs to simulator session pointers and mutates the singleton connection/session timestamp state. It reads but does not write files.

Dependencies and integration points: depends on `nlohmann::json`, `call_log_manager.h`, `connection_simulator`, and exact call-log schema keys such as `method_name`, `class_name`, `session_id`, `input`, `output`, and `return`.

Risks: several thrown expressions are string concatenations from string literals and may not be caught by `catch (std::string&)` as intended. `assert` checks disappear in release builds, reducing mismatch detection. Unknown `method_name` uses `_api_map.at` and can throw outside the switch-specific handling.

Test signals: successful replay with no assertion failure validates simulator agreement with the call log; query timestamp entries additionally compare returned hex timestamps when supported.
