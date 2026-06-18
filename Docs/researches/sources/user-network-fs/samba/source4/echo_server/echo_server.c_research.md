# sources/user-network-fs/samba/source4/echo_server/echo_server.c

## Purpose

`echo_server.c` implements Samba's example echo server service. When enabled for selftest, it registers a `service` subsystem module that listens for UDP echo packets on configured interfaces and sends each payload back unchanged.

## Important APIs, Types, and Functions

Key structures are `echo_socket`, `echo_udp_socket`, and `echo_udp_call`. `echo_process()` copies input `DATA_BLOB` bytes to an output blob. `echo_udp_call_loop()` receives datagrams asynchronously, calls `echo_process()`, and schedules replies. `echo_udp_call_sendto_done()` frees per-call state after send completion. `echo_add_socket()` binds a UDP socket and starts the receive loop. `echo_startup_interfaces()` binds each configured interface. `echo_task_init()` decides whether the service runs and initializes service state. `server_service_echo_init()` registers the service details.

## Control Flow

Service registration points the Samba process model at `echo_task_init()`. The task starts only for standalone and AD DC roles, loads the interface list, allocates `struct echo_server`, then calls `echo_startup_interfaces()`. For each interface, `echo_add_socket()` creates a `tsocket_address`, binds a `tdgram` UDP socket, creates a tevent send queue, and posts a `tdgram_recvfrom_send()`. Each receive callback processes one packet, queues a send response to the sender, and immediately posts the next receive operation.

## State and Persistence Behavior

State is entirely in memory and talloc-scoped beneath the task and socket objects. Each UDP packet gets a temporary `echo_udp_call` containing source address, input blob, and output blob; the call is freed when send completes or on failure. There is no durable storage, authentication state, or protocol session state beyond the asynchronous send queue.

## Dependencies and Integration Points

The implementation integrates with Samba's process model, `task_server` lifecycle, loadparm server role, network interface discovery, `tsocket`/`tdgram`, tevent callbacks and queues, NTSTATUS error handling, and service registration. It uses `ECHO_SERVICE_PORT` from `echo_server.h` and is built as the `ECHO` service module by the echo server Waf file.

## Risks and Edge Cases

The service binds port 7 on all configured interfaces, which may require privileges or conflict with an existing echo service. It ignores UDP send errors, appropriate for a sample server but weak for diagnostics. Receive-loop rearming happens even after many failure cases, but allocation failure terminates the task. The `name` and `model_ops` parameters in `echo_add_socket()` are unused, reflecting example-code heritage.

## Test Signals

Signals include successful service registration under selftest builds, startup in standalone or AD DC roles but not domain-member role, UDP bind success for each configured interface, and byte-for-byte UDP echo responses for arbitrary datagrams.
