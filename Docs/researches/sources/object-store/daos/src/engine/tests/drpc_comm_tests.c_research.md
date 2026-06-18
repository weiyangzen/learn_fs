# sources/object-store/daos/src/engine/tests/drpc_comm_tests.c

Purpose: cmocka integration tests for the user-facing dRPC communication stack using a simplified in-process test listener. It verifies basic, large single-chunk, and chunked request/response traffic.

Important APIs and functions: `run_hello_test()` connects with `drpc_connect()`, creates a call with `drpc_call_create()`, packs a `Hello__Hello` protobuf body, issues `drpc_call(ctx, R_SYNC, ...)`, unpacks `Hello__HelloResponse`, and compares it with `get_greeting()`. `gen_str()` creates deterministic long names. `DRPC_COMM_TEST` runs each test with `drpc_listener_setup()` and `drpc_listener_teardown()`.

Control flow: each test starts a temporary listener, connects a client to its socket, sends a greeting request, validates `DRPC__STATUS__SUCCESS`, verifies response payload, frees protobuf/dRPC resources, and closes the client context. The long tests size inputs around `UNIXCOMM_MAXMSGSIZE` to exercise chunk boundaries.

State and persistence: per-test state is `struct drpc_test_state` owned by the listener helper. Temporary socket directory and socket path are created under `/tmp` and removed during teardown.

Dependencies and integration: depends on public dRPC APIs, generated `drpc_test.pb-c.h`, `drpc_test_listener.[ch]`, and DAOS test logging. It validates end-to-end framing, chunking, protobuf body preservation, and synchronous call behavior.

Risks: tests rely on `/tmp`, pthread scheduling, and local Unix sockets, so they are more integration-like than pure unit tests. `gen_str()` assumes `len > 0`. The listener helper assumes a simple single-threaded client model.

Test signals: suite name `drpc_comms`; important signals are success for normal name, name of size `CHUNK_SIZE / 2`, and name of size `CHUNK_SIZE`, with successful cleanup of call, response, dRPC context, socket, and directory.
