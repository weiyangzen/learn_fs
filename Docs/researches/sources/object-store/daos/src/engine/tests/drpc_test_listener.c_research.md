# sources/object-store/daos/src/engine/tests/drpc_test_listener.c

Purpose: simplified dRPC listener used by `drpc_comm_tests.c` to run integration-style communication tests without the full DAOS engine stack.

Important APIs and functions: `get_greeting()` formats `"Hello <name>"`. `hello_handler()` validates hello module/method, unpacks `Hello__Hello`, packs `Hello__HelloResponse`, and fills the dRPC response body. `drpc_listener_setup()` creates a temporary directory/socket path and starts the listener. `drpc_listener_teardown()` stops the pthread listener, closes dRPC progress context, removes socket and directory, and frees state. `dss_ult_create()` is stubbed to execute the function synchronously.

Control flow: setup creates `/tmp/drpc_test.XXXXXX`, starts `drpc_listen()` with `hello_handler`, wraps it in `drpc_progress_context_create()`, marks the listener running, and launches a pthread running `run_test_listener()`. The thread loops on `drpc_progress(..., 500)` until `listener_running` is cleared, ignoring `-DER_TIMEDOUT`. Teardown clears the flag, joins the thread, closes dRPC state, and removes filesystem artifacts.

State and persistence: `struct drpc_test_state` owns the progress context, temp directory, socket path, pthread, mutex, and running flag. Filesystem state is temporary under `/tmp` and removed on teardown. Synchronization uses a pthread mutex around the running flag.

Dependencies and integration: depends on pthreads, Argobots type compatibility, dRPC internals, DAOS test logging, and generated hello protobuf code. It bridges public dRPC client calls to real `drpc_progress()` behavior in tests.

Risks: the synchronous `dss_ult_create()` stub collapses production ULT concurrency into direct calls, so it cannot expose scheduling races. `pthread_create()` is checked with `< 0`, but POSIX returns nonzero positive error codes, so failure detection is incomplete. Teardown assumes setup reached a valid listener state.

Test signals: used by `drpc_comm_tests.c`; signals are successful temporary directory/socket creation, listener thread progress, correct hello response packing, clean stop/join, and removal of socket and temp directory.
