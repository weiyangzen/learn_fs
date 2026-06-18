# File Research: sources/virtualization/open-iscsi/usr/login.c

Purpose: Implements the iSCSI login negotiation engine used by userspace initiator paths. It builds Login Request PDUs, parses Login Response PDUs, negotiates security and operational text keys, handles target redirection, and drives the request/response loop until full-feature phase or failure.

Key entry points:
- `iscsi_add_text()` appends NUL-terminated `key=value` text entries to an iSCSI PDU data segment and updates the 24-bit data length field.
- `resolve_address()` wraps `getaddrinfo()` for target address resolution into `sockaddr_storage`.
- `iscsi_update_address()` parses `TargetAddress` values, including optional portal-group tag and bracketed IPv6 address, then updates the connection socket address and session TPGT.
- `iscsi_login_begin()`, `iscsi_login_req()`, and `iscsi_login_rsp()` expose a split login state machine for callers that manage polling externally.
- `iscsi_login()` is the synchronous login loop: make request, send PDU, poll the connection, receive/process response, and repeat until `ISCSI_FULL_FEATURE_PHASE`.

Implementation notes:
- Text-key parsing is exact-prefix based via `iscsi_find_key_value()`, which returns the value span within the received text data. `iscsi_process_login_response()` ensures a trailing NUL by requiring a receive buffer larger than the PDU data length.
- Security-stage keys are split between initiator-visible keys (`TargetAlias`, `TargetAddress`, `TargetPortalGroupTag`) and authentication-library keys selected through `acl_get_next_key_type()` and consumed with `acl_recv_key_value()`.
- Operational negotiation recognizes standard iSCSI keys such as `InitialR2T`, `ImmediateData`, burst lengths, digests, marker settings, ordering, `MaxConnections`, `ErrorRecoveryLevel`, and RDMA-specific keys. Unsupported or unacceptable values map to login-status failures rather than silent downgrade.
- Discovery sessions mark normal-session-only keys as irrelevant and later answer with `key=Irrelevant` using `session->irrelevant_keys_bitmap`.
- Digest negotiation supports strict `None`, strict `CRC32C`, and ordered preference lists (`None,CRC32C` or `CRC32C,None`) when constructing outbound login text.
- RDMA transports use `InitiatorRecvDataSegmentLength`, `TargetRecvDataSegmentLength`, and `RDMAExtensions`; non-RDMA and discovery use `MaxRecvDataSegmentLength`.
- Authentication setup initializes ACL buffers, username/password, CHAP algorithm list, IPsec flag, and bidirectional-auth policy from `iscsi_session_t`.
- Response validation checks active iSCSI version, current-stage consistency, transit-bit stage advancement, login opcode, and old draft-8 opcode mismatch.

Dependencies and interactions:
- Uses `initiator.h` session/connection state, `transport.h` transport properties, `log.h`, and `iscsi_timer.h`.
- Calls lower I/O functions `iscsi_io_send_pdu()` and `iscsi_io_recv_pdu()` through the connection.
- Uses authentication functions from the ACL/auth layer (`acl_init`, `acl_send_*`, `acl_recv_*`, `acl_finish`, CHAP helpers).
- Updates session command/status sequence numbers (`cmdsn`, `exp_cmdsn`, `max_cmdsn`, `tsih`) from accepted login responses.

Filesystem/storage relevance:
- This file is the userspace control-plane gateway that turns an iSCSI node record and transport connection into an authenticated, negotiated storage session. Storage parameters negotiated here determine later SCSI command limits, data segment sizes, digest enforcement, and error-recovery behavior.
