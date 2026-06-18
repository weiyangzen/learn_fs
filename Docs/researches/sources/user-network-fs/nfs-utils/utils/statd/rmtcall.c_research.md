## sources/user-network-fs/nfs-utils/utils/statd/rmtcall.c

Purpose: Sends asynchronous local callbacks to lockd after peer reboot notifications and processes replies on a reserved UDP socket.

Important APIs/types/functions: `statd_get_socket`, `recv_rply`, `process_entry`, `process_reply`, and `process_notify_list`. It uses `nsm_xmit_getport`, `nsm_recv_getport`, `nsm_xmit_nlmcall`, and `nsm_parse_reply`.

Control flow: A privileged loopback UDP socket is created before dropping privileges. Pending entries first discover the local lockd port if needed, then send the callback RPC. Replies are matched by XID, update callback port, reschedule entries, or free successful/failed entries. Timeouts reinsert entries by `NL_WHEN` until retries are exhausted.

State and persistence: Uses static `sockfd` and the global `notify` list. No persistent state.

Dependencies and integration: Integrated with `svc_run.c` select loop and `callback.c`/`monitor.c` queue producers; depends on reserved ports accepted by lockd.

Risks and test signals: Only loopback replies are trusted, but XID collisions and retry exhaustion need coverage. Tests should exercise reserved-port binding, service port discovery, successful callback, no registered service, timeout rescheduling, and failure after `MAX_TRIES`.
