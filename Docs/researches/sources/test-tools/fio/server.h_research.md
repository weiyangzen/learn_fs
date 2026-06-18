# sources/test-tools/fio/server.h

## Purpose
`server.h` defines fio's network protocol contract and public server API. It is the shared header for encoding/decoding server commands, payload structures, feature flags, and server-mode function entry points.

## Important APIs, Types, And Functions
`struct sk_out` describes a server output channel: reference count, socket fd, lock, pending transmit list, wait semaphore, and transmit semaphore. `struct fio_net_cmd` is the wire header with protocol version, opcode, flags, tag, payload length, command CRC, payload CRC, and flexible payload. The comment states that on-wire encoding is little-endian.

The command enum defines `FIO_SERVER_VER`, fragmentation and maximum command limits, all `FIO_NET_CMD_*` opcodes, `FIO_NET_CMD_F_MORE`, CRC coverage size, name limits, timeout, and probe flags. Payload structs include job/jobline/load-file PDUs, text output, thread-stat and disk-util PDUs, probe request/reply, start/end messages, iolog descriptors, sendfile replies, and job option notifications.

Exports include startup/configuration (`fio_start_server()`, `fio_server_set_arg()`, `fio_server_internal_set()`), parsing (`fio_server_parse_string()`, `fio_server_parse_host()`), transport (`fio_net_send_cmd()`, `fio_net_send_simple_cmd()`, `fio_net_recv_cmd()`, `fio_server_poll_fd()`, `fio_net_send_quit()`), output (`fio_server_text_output()`, `fio_server_send_ts()`, `fio_server_send_gs()`, `fio_server_send_du()`, `fio_send_iolog()`), job notifications, verify-state retrieval, and socket-key lifecycle.

## Control Flow
Callers configure the bind string, initialize the socket key, and start the server. During runtime, backend code uses the exported send functions to serialize stats/logs to the connected client. Client and server agree on opcodes and PDU layouts through this header; `server.c` performs endian conversion before sending and after receiving.

## State And Persistence Behavior
The header exposes `exit_backend` and `fio_net_port`, making server shutdown and port configuration globally visible. The protocol embeds variable-length data with flexible arrays, so payload lifetime and size are managed by callers rather than the header itself.

## Dependencies And Integration Points
It includes `stat.h` and `diskutil.h` because network payloads embed `thread_stat`, `group_run_stats`, and disk-util data. It also requires socket address types and fio sem/list definitions indirectly through included project headers.

## Risks And Edge Cases
Packed or flexible payload structs are ABI-sensitive. Any change to `FIO_SERVER_VER`, `thread_stat`, `group_run_stats`, or payload field order requires matching conversion code and client support. The typo in the `pdu_len` comment is harmless, but it highlights that comments should not be treated as protocol proof. Fixed name/value arrays in `cmd_job_option` can truncate data and rely on explicit truncation flags.

## Test Signals
Compile-time protocol tests should ensure struct sizes/offsets match client decode expectations. Runtime tests should cover each opcode, payload fragmentation, CRC failures, little/big endian conversion, zlib probe negotiation, and older-client version rejection.
