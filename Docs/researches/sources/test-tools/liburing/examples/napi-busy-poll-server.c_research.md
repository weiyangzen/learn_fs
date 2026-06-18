# sources/test-tools/liburing/examples/napi-busy-poll-server.c

## sources/test-tools/liburing/examples/napi-busy-poll-server.c

Purpose: UDP ping/pong server companion for the NAPI busy-poll client.

Important APIs/types/functions: `struct ctx`, global `opt`, `io_uring_napi`; `receivePing`, `sendPing`, `completion`, `reportNapi`; `io_uring_prep_recvmsg`, `io_uring_prep_sendmsg`, `io_uring_register_napi`.

Control flow: parse listen/address/port/count/NAPI options, bind UDP socket, initialize ring with taskrun mode, optionally register NAPI preferences, optionally set SCHED_FIFO, arm initial `recvmsg`, then loops on `io_uring_submit_and_wait_timeout`. Each recv stores peer address and received length then queues sendmsg echo; each send decrements remaining ping count and rearms receive.

State and persistence: socket bind state, current message/iovec buffers in `ctx`, NAPI registration. No persistent files.

Dependencies/integration: works with client example, liburing NAPI APIs, UDP IPv4/IPv6 sockets, optional realtime scheduling.

Risks: same fixed-buffer `strcpy` risk as client. `--listen` is parsed but mandatory server behavior does not require it. Some options declared as no-arg are parsed as needing optional data in code. Error handling often aborts.

Test signals: server logs listening address and NAPI id; paired client receives replies and reports RTT.
