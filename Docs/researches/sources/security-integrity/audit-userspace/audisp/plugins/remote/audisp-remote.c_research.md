# sources/security-integrity/audit-userspace/audisp/plugins/remote/audisp-remote.c

Purpose: implements the remote audit dispatcher plugin that queues audit records and forwards them to a central logger over TCP or Kerberos/GSSAPI.

Important APIs and data: main daemon state includes signal flags, socket state, `remote_conf_t config`, persistent/in-memory queue, and max queue depth tracking. Key paths are `init_queue`, `send_one`, `relay_event`, `relay_sock_managed`, `relay_sock_ascii`, `init_transport`, `stop_transport`, `check_message`, and failure-action handlers.

Control flow: main loads `/etc/audit/audisp-remote.conf`, initializes queue, optionally drops capabilities, and enters a `select` loop over stdin and remote socket. Incoming audit lines are stripped of EOE records, appended to the queue, and sent when the socket is writable. Managed format sends headers, waits for matching ACK/status response, retries within configured count/time limits, and handles remote disk/ending/errors. ASCII format writes raw records without ACK protocol.

State and persistence: immediate mode uses memory queue only; store-and-forward uses `queue.c` file storage under configured `queue_file` or `/var/spool/audit/remote.log`. Signal state supports SIGHUP reload, SIGUSR1 state dump to `remote.state`, SIGUSR2 resume, SIGTERM from parent only, and SIGCHLD reaping.

Dependencies and integration: depends on auplugin input, libaudit remote managed wire macros, `remote-config.c`, `queue.c`, syslog, optional cap-ng, optional GSSAPI/Kerberos, and runlevel changes for severe actions.

Risks: failure actions can suspend logging, stop the plugin, switch runlevel, or halt the host. Managed mode correctness relies on sequence numbers and sync recovery. GSS keytab permission checks are strict. Store-and-forward durability depends on queue file semantics and does not sync each entry unless queue flags change.

Test signals: `test-queue` covers queue mechanics; protocol tests should simulate ACKs, remote disk low/full/error, ending messages, retry exhaustion, heartbeat, SIGHUP, overflow, and store-forward restart.
