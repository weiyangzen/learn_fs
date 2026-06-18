# sources/storage-engines/wiredtiger/test/simulator/timestamp/call_log_manager/call_log_manager.h

Purpose: declares the call-log replay manager and its mapping from logged WiredTiger API method names to simulator method handlers.

Important APIs and control flow: `enum class api_method` enumerates supported call-log methods. `call_log_manager` exposes a constructor taking a call-log file path and `process_call_log()`. Private helpers set up `_api_map`, retrieve sessions by logged ID, and implement one handler per supported method.

State and persistence behavior: owns a raw pointer to the connection singleton, parsed JSON call log, method-name map, and session-ID-to-session-pointer map. Session lifetime is controlled by forwarding open/close operations to `connection_simulator`.

Dependencies and integration points: includes `connection_simulator.h` and `nlohmann/json.hpp`. It is consumed only by the call-log executable.

Risks: raw session pointers require `_session_map` to stay synchronized with connection lifetime. The header uses `using json = nlohmann::json` globally, which leaks an alias to includers.

Test signals: compile-time coverage of all declared handlers and replay coverage for each enum value show schema/API alignment.
