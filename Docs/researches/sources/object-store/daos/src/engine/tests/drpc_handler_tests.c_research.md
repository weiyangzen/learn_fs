# sources/object-store/daos/src/engine/tests/drpc_handler_tests.c

Purpose: cmocka unit tests for the dRPC handler registry and message dispatch layer.

Important APIs and functions: helper `create_handler_list()` builds null-terminated arrays of `struct dss_drpc_handler`; dummy handlers provide distinct function pointers. Tests exercise `drpc_hdlr_init()`, `drpc_hdlr_fini()`, `drpc_hdlr_register()`, `drpc_hdlr_unregister()`, `drpc_hdlr_register_all()`, `drpc_hdlr_unregister_all()`, `drpc_hdlr_get_handler()`, and `drpc_hdlr_process_msg()`.

Control flow: setup initializes the registry and dRPC handler mocks for most tests. Registration tests validate bad input, duplicate module IDs, invalid module IDs, multiple handlers, and unchanged registry entries after failed operations. Dispatch tests create a `Drpc__Call` and `Drpc__Response`, register or omit a mock handler, and validate handler invocation or `DRPC__STATUS__UNKNOWN_MODULE`. Uninitialized tests intentionally skip setup.

State and persistence: registry state is process-local and reset by setup/teardown. Handler arrays are heap allocated only inside helper tests and freed before return.

Dependencies and integration: uses generated `drpc.pb-c.h`, dRPC module IDs, DAOS mocks, and `drpc_handler.h`. It defines the expected semantics for engine modules that register dRPC control handlers.

Risks: bulk registration with a duplicate expects earlier entries to remain registered, so callers must treat `-DER_EXIST` as partial failure. Tests do not cover concurrent registration or unregister during dispatch. The helper assumes module IDs start at zero for its generated lists.

Test signals: suite name `engine_drpc_handler`; strong signals include null handler rejection, duplicate protection, invalid ID rejection, idempotent unregister of missing IDs, all-list operations, successful dispatch copying mock response fields, unknown-module status, and `-DER_UNINIT` behavior before initialization.
