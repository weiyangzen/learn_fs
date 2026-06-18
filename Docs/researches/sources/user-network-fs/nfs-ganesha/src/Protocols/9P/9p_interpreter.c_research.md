## sources/user-network-fs/nfs-ganesha/src/Protocols/9P/9p_interpreter.c

Purpose: dispatches 9P messages from decoded connection buffers to individual handlers.

APIs and flow: `_9pfuncdesc` maps 9P opcodes to handlers and names. `_9p_process_buffer` reads message length/type, bounds checks opcode, sets max reply length to negotiated `msize`, calls the service handler, records 9P stats, and releases op context. `_9p_tcp_process_request` wraps processing and sends replies with `tcp_conn_send`, which serializes socket writes and records transport stats. `_9p_not_2000L` returns `ENOTSUP` for unsupported legacy 9P2000 operations.

State/dependencies: uses per-request `_9p_request_data`, per-connection `msize`, socket lock, flush hook cleanup, server stats, and common op context lifecycle.

Risks/tests: opcode table holes, incorrect max reply sizing, socket short writes, and forgotten op context release are core risks. Test all known opcodes, unsupported opcodes, small msize, concurrent TCP replies, and stats accounting.
