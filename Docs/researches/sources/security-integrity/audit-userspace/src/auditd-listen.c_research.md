# sources/security-integrity/audit-userspace/src/auditd-listen.c

## Purpose
`auditd-listen.c` implements auditd's remote aggregation TCP listener. It accepts remote audit records, optionally negotiates Kerberos/GSSAPI security, turns received messages into `auditd_event` objects, and sends protocol acknowledgements after local handling.

## Important APIs, Types, And Functions
Public functions are `auditd_tcp_listen_init`, `auditd_tcp_listen_uninit`, `auditd_tcp_listen_reconfigure`, and `write_connection_state`. Key internal pieces are `ev_tcp`, socket/address helpers, `client_ack`, `client_message`, `auditd_tcp_client_handler`, `auditd_tcp_listen_handler`, `check_num_connections`, idle `periodic_handler`, and GSS token/credential helpers under `USE_GSSAPI`.

## Control Flow
Initialization resolves wildcard bind addresses, creates up to four listener sockets, chooses IPv6 preference when appropriate, binds/listens, registers libev IO watchers, starts idle timers, applies configured source port and per-address limits, and acquires GSS credentials if needed. Accept flow applies libwrap, source port range, duplicate connection limits, socket options, optional GSS negotiation, nonblocking mode, and list insertion. Read flow handles GSS tokens, RMW framed messages, or newline-delimited messages, then creates remote events or responds to heartbeats.

## State And Persistence
Module globals track listener sockets, count, libev watchers, allowed ports, libwrap flag, transport mode, receive buffer, linked client list, and GSS server credentials. No on-disk persistence is owned here, but accepted/closed connections emit audit daemon events and remote events may be persisted by `auditd-event.c`.

## Dependencies And Integration
It depends on sockets, netdb, libev, optional libwrap, optional GSSAPI/Kerberos, `libaudit`, `auditd-event.h`, and `auditd-config.h`. It calls `send_audit_event`, `create_event`, `distribute_event`, and network ack callbacks.

## Risks
Risks include blocking GSS negotiation inside an otherwise nonblocking listener, buffer/length handling for mixed protocols, remote event type extraction later in `auditd.c`, trust assumptions around firewall plus source port checks, per-address IPv4/IPv6 comparison correctness, and partial live reconfigure behavior for listener port/transport changes that require restart.

## Test Signals
No focused listener unit test appears in `src/test`, though `format_event_test` can link `auditd-listen.c` when listener support is enabled. Useful tests would simulate framed/newline/GSS message parsing, heartbeat ack, idle timeout, libwrap rejection, port range rejection, and reconfigure of queue/port settings.
