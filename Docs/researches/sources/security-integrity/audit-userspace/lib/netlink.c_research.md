# sources/security-integrity/audit-userspace/lib/netlink.c

Purpose: low-level libaudit transport for the kernel audit netlink protocol. It opens/closes `NETLINK_AUDIT`, sends audit requests, receives replies, validates message origin and size, and maps netlink payloads into `struct audit_reply` convenience pointers.

Important APIs: `audit_open`, `audit_close`, `audit_get_reply`, `__audit_send`, and `audit_send`. Internal helpers are `adjust_reply` and `check_ack`.

Control flow: `audit_open` creates a close-on-exec raw netlink socket. `__audit_send` validates fd and payload size, assigns a static sequence number, constructs `struct audit_message`, sends to kernel pid 0, then waits for an ACK through `check_ack`. `audit_get_reply` receives, retries on `EINTR`, rejects spoofed nonzero `nl_pid`, and delegates payload interpretation to `adjust_reply`.

State and persistence: uses a process-local static sequence counter in `__audit_send`; no disk persistence. It mutates `errno` to communicate protocol errors and adjusts pointer fields inside the caller-owned reply structure.

Dependencies and integration: depends on `libaudit.h`, `private.h`, Linux netlink macros, `poll`, `recvfrom`, and `sendto`. Higher-level APIs in libaudit and `auditctl.c` use this file to change kernel audit status and rules.

Risks and test signals: the static sequence counter is not synchronized for concurrent callers. `check_ack` polls up to about 40 seconds and peeks before consuming `NLMSG_ERROR`; behavior depends on kernel ACK timing. Important security checks are NLMSG validation and kernel-origin enforcement. Integration tests require a live audit-capable kernel and privileges.
