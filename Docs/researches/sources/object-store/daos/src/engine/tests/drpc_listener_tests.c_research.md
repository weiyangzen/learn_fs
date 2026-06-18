# sources/object-store/daos/src/engine/tests/drpc_listener_tests.c

Purpose: cmocka unit tests for engine dRPC listener initialization and finalization.

Important APIs and functions: mocks capture `dss_ult_create()` parameters, `drpc_progress_context_create()` listener details, and `drpc_progress_context_close()` calls. Tests call `drpc_listener_init()` and `drpc_listener_fini()` while syscall and ABT mocks simulate socket, bind/listen, mutex, thread join/free, and unlink behavior.

Control flow: initialization tests validate socket creation failure, successful socket path construction (`dss_socket_dir/daos_engine_<pid>.sock`), unlink before listen, progress context creation with `drpc_hdlr_process_msg`, mutex creation, and listener ULT creation on target/xstream 0. Failure paths cover progress-context allocation, ABT mutex creation, and ULT creation cleanup. Finalization tests cover successful thread join/free/mutex free and each ABT failure mapping to DAOS errors.

State and persistence: the test owns mock globals and may allocate `drpc_listener_socket_path`; teardown frees leftover path and test progress context. No durable state is intended, but the real code path would create and unlink a Unix socket path.

Dependencies and integration: includes `drpc_internal.h`, DAOS test mocks, and ABT stubs. It verifies the integration boundary between listener socket setup, dRPC progress context, handler dispatch, and Argobots listener ULT lifecycle.

Risks: tests use stubs for `drpc_progress()` and handler lookup/dispatch, so they do not validate actual progress behavior. The captured `dss_ult_create_stream_id` stores the target argument, not the full ULT type, so the test focuses on target zero and stack/handle outputs. Cleanup must avoid double-freeing the listener pointer after failure.

Test signals: suite name `engine_drpc_listener`; expected signals are correct socket path/unlink/listen, non-null mutex and ULT handle pointer, context close on ULT creation failure, and precise DAOS return mapping for ABT join/free/mutex failures.
