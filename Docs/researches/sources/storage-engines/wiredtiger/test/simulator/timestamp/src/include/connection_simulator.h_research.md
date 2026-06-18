# sources/storage-engines/wiredtiger/test/simulator/timestamp/src/include/connection_simulator.h

Purpose: declares the singleton connection simulator API and global timestamp/session state.

Important APIs and control flow: public methods expose `get_connection`, session open/close, `set_timestamp`, global durable setter/getters, oldest/stable presence checks, latest active read timestamp, and `query_timestamp`. Private `decode_timestamp_config_map()` extracts parsed set-timestamp fields. Copy and assignment are deleted.

State and persistence behavior: private members are a vector of owned `session_simulator*` plus oldest, stable, and durable timestamps. State is process-local and reset only by process restart.

Dependencies and integration points: includes `session_simulator.h` and is included by frontends and session/timestamp validation code.

Risks: singleton design makes tests order-dependent if multiple replay/interface operations run in one process. Raw pointer ownership is visible through the API and requires clients not to delete sessions directly.

Test signals: compile and replay coverage of all getters/setters and session lifecycle calls.
