<!-- BEGIN_FILE_RESEARCH: sources/test-tools/filebench/multi_client_sync.h -->
# sources/test-tools/filebench/multi_client_sync.h

Purpose: declares the multi-client synchronization client API.

Important APIs: `mc_sync_open_sock(char *master_name, int master_port, char *client_name)` establishes the TCP connection. `mc_sync_synchronize(int synch_point)` blocks until the external master releases a sync point.

Control flow contract: parser code calls open before synchronize; callers receive Filebench status codes.

State/persistence: implementation stores one static socket/client identity per process.

Dependencies/integration: conditionally includes socket headers based on configuration and is used by `parser_gram.y`.

Risks: the API does not expose close/reset, timeout, or error detail, which limits recovery after sync server failure.

Test signals: compile with/without `HAVE_SYS_SOCKET_H` and parser-level WML tests for `enable multi` plus `domultisync`.
<!-- END_FILE_RESEARCH: sources/test-tools/filebench/multi_client_sync.h -->
