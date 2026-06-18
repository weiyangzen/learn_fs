# sources/object-store/daos/src/engine/tests/drpc_test_listener.h

Purpose: header declaring the simplified dRPC test listener contract shared by `drpc_comm_tests.c` and `drpc_test_listener.c`.

Important APIs and types: `struct drpc_test_state` holds `struct drpc_progress_context *progress_ctx`, temporary directory and socket path strings, a listener pthread, a mutex, and a boolean running flag. Public helper declarations are `get_greeting()`, `drpc_listener_setup()`, and `drpc_listener_teardown()`.

Control flow: cmocka tests use the setup/teardown functions as per-test fixtures. The state struct carries the socket path used by the dRPC client and the listener thread/progress context used by teardown.

State and persistence: defines ownership fields but does not allocate itself. The implementation owns lifecycle and temporary `/tmp` artifacts.

Dependencies and integration: includes pthread and `drpc_internal.h` for progress context definitions. Integrated directly by dRPC communication tests.

Risks: the header exposes internal listener state to tests, so tests can depend on implementation details. It includes dRPC internals rather than a narrow public forward declaration.

Test signals: compile-time signal is that the shared fixture shape matches the implementation and communication tests; runtime signals come from the `.c` implementation.
