# sources/storage-engines/wiredtiger/test/simulator/timestamp/simulator_interface/simulator_interface.h

Purpose: declaration header for the interactive timestamp simulator CLI.

Important APIs and control flow: declares ANSI color macros, generic CLI helpers (`choose_num`, `print_border_msg`, `print_options`, `get_input`, `get_session`), session-management entry point, connection-level timestamp operations, session-level transaction operations, and `print_rules()`.

State and persistence behavior: the header stores no state. Declared functions operate on `connection_simulator*`, `session_simulator*`, and a caller-owned session map.

Dependencies and integration points: includes STL containers/strings and `connection_simulator.h`; consumed by `simulator_interface.cpp`.

Risks: color macros are global preprocessor definitions and can collide with other code if reused more widely. Function declarations expose raw session pointers consistent with the simulator library.

Test signals: compile coverage ensures the frontend and simulator library APIs remain aligned.
