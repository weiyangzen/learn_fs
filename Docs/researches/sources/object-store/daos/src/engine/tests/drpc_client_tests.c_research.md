# sources/object-store/daos/src/engine/tests/drpc_client_tests.c

Purpose: cmocka unit tests for engine-to-agent dRPC client helpers. The tests validate dRPC call failure handling and the protobuf payloads sent by readiness, pool service update, and RAS cluster-event notifications.

Important APIs and functions: test mocks provide `crt_self_uri_get()`, `crt_self_incarnation_get()`, `crt_group_rank()`, `get_module_info()`, and scheduler stubs expected by engine notification code. `drpc_client_test_setup()` initializes socket syscall mocks and `drpc_init()`. `unpack_sendmsg_drpc_call()` decodes the mocked `sendmsg` buffer after the dRPC header. Verification helpers inspect `Srv__NotifyReadyReq` and `Shared__ClusterEventReq` protobuf messages. Tests call `dss_drpc_call()`, `drpc_notify_ready()`, `ds_notify_pool_svc_update()`, and `ds_notify_ras_event()`.

Control flow: each test sets mock syscall return values or a valid dRPC response, invokes a notification helper, and inspects return codes, close counts, send counts, and unpacked protobuf fields. Negative tests force chmod/connect/send failures and invalid pool service update arguments.

State and persistence: all state is mock global state: fake socket paths, hostname, dss xstream counts, mock CART URI/incarnation/rank, and captured socket buffers. No durable state is modified.

Dependencies and integration: includes `drpc_internal.h`, generated `srv.pb-c.h` and `event.pb-c.h`, dRPC module IDs, DAOS test mocks, and engine globals. It verifies the protocol contract between DAOS engine notification code and the control-plane agent over a Unix-domain dRPC socket.

Risks: because the test decodes the raw `sendmsg` mock buffer, it is sensitive to dRPC framing changes. The mocked `get_module_info()` allocates one module-info object and relies on teardown freeing it. The tests cover successful packing and selected syscall errors, but not malformed dRPC responses or retry timing.

Test signals: suite name `engine_drpc_client`; expected coverage includes socket close on failures, no send for invalid pool service update or empty RAS messages, correct readiness fields (`uri`, `nctxs`, listener socket, instance index, target count), and correct cluster-event metadata/defaults.
