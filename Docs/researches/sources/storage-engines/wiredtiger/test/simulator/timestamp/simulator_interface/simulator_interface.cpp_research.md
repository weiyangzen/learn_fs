# sources/storage-engines/wiredtiger/test/simulator/timestamp/simulator_interface/simulator_interface.cpp

Purpose: interactive console frontend for the timestamp simulator. It lets a user create/use sessions, set/query connection timestamps, begin/commit/prepare/rollback transactions, set transaction timestamps, query session timestamps, and print rule summaries.

Important APIs and control flow: helper functions print colored bordered messages, list numbered options, parse numeric choices from stdin, collect free-form input, and retrieve sessions from a map. `interface_session_management()` lists sessions, switches active session, or opens a new one. Connection-level functions build `set_timestamp` and `query_timestamp` configs. Session-level functions incrementally build config strings then execute simulator methods. `main()` creates a connection singleton, opens `Session1`, maintains `session_map` and `session_in_use`, and loops over the main menu until exit.

State and persistence behavior: process state includes the simulator singleton, session map, active session name, and in-progress config strings. No files or databases are written.

Dependencies and integration points: includes `simulator_interface.h` and uses `connection_simulator`/`session_simulator`. Output uses ANSI color constants declared in the header.

Risks: input validation only bounds parsed integers; nonnumeric input can reuse an uninitialized `choice` value if extraction fails. Config string assembly appends commas after each selected option, relying on the parser to ignore empty tokens. Session close is not exposed, so created sessions live until process exit.

Test signals: manual runs should show expected success/error messages for timestamp rule examples and query paths.
