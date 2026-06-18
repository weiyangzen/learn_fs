<!-- BEGIN_FILE_RESEARCH: sources/test-tools/filebench/multi_client_sync.c -->
# sources/test-tools/filebench/multi_client_sync.c

Purpose: implements a simple TCP client for coordinating multi-client Filebench runs with an external synchronization master.

Important APIs/functions: `mc_sync_open_sock(master_name, master_port, my_name)` stores the client name, creates a TCP socket, binds locally, resolves the master with `gethostbyname()`, and connects. `mc_sync_synchronize(sync_point)` sends a `cmd=SYNC` message including client name and sample number, then waits for a newline-terminated reply.

Control flow: parser command `enable multi` opens the socket, and `domultisync` calls synchronize at WML-defined points. Success is logged and `FILEBENCH_OK` is returned; socket/bind/connect errors log and return `FILEBENCH_ERROR`.

State/persistence: static `mc_sync_sock_id` and `this_client_name` persist for the process. The socket remains open for later sync points.

Dependencies/integration: uses BSD sockets, DNS, parser multi-client commands, Filebench logging/status constants, and `multi_client_sync.h`.

Risks: no null check after `gethostbyname()`. `strncpy()` may leave `this_client_name` unterminated for long names. The receive loop repeatedly writes at the start of `msg`, does not reserve space for a terminator, does not handle `recv()` returning 0/-1, and can spin or overcount. Socket is not closed.

Test signals: integration with a fake sync server, DNS failure, refused connection, partial replies, missing newline, long client names, and repeated sync points.
<!-- END_FILE_RESEARCH: sources/test-tools/filebench/multi_client_sync.c -->
