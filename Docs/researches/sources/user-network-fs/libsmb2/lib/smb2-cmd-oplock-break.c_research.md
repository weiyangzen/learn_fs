<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libsmb2/lib/smb2-cmd-oplock-break.c -->
# sources/user-network-fs/libsmb2/lib/smb2-cmd-oplock-break.c

## Purpose

`smb2-cmd-oplock-break.c` implements SMB2 OPLOCK_BREAK and lease-break acknowledgements, replies, and notifications. It handles both classic oplock structures and SMB2 lease structures under the same command.

## Important APIs, Types, And Functions

Public functions include `smb2_cmd_oplock_break_async`, `smb2_cmd_oplock_break_reply_async`, `smb2_cmd_oplock_break_notification_async`, `smb2_cmd_lease_break_async`, `smb2_cmd_lease_break_reply_async`, `smb2_cmd_lease_break_notification_async`, `smb2_process_oplock_break_fixed`, `smb2_process_oplock_break_variable`, `smb2_process_oplock_break_request_fixed`, and `smb2_process_oplock_break_request_variable`. Payloads are union wrappers for oplock and lease break request/reply variants.

## Control Flow

Encoders allocate an OPLOCK_BREAK PDU and choose body size based on oplock acknowledgement/reply/notification or lease acknowledgement/reply/notification. Fixed parsing first reads only the struct size, allocates a generic wrapper, and returns the remaining byte count for that variant. Variable parsing then decodes fields with offsets adjusted because the struct size was consumed as the fixed part. Unsolicited oplock notifications are distinguished by message ID `0xffffffffffffffff`.

## State And Persistence Behavior

Local state is transient in PDU payloads. Protocol state affects client caching guarantees: oplock/lease breaks require clients to downgrade cached access and acknowledge. `pdu.c` has special correlation logic for unsolicited `SMB2_OPLOCK_BREAK` notifications.

## Dependencies And Integration Points

The file depends on PDU helpers and oplock/lease constants. It integrates tightly with open/create lease state and server async notification handling.

## Risks And Edge Cases

Several lease encoders write multiple fields at offset 4 instead of their distinct wire offsets, so encoded lease acknowledgements and notifications appear corrupt. In lease reply variable parsing, the lease key is copied into `rep->lock.lease.lease_key` rather than the `leaserep` member, which may indicate a union/member mistake. Error text contains typos but more importantly fixed parsing trusts the receive layer to provide the exact remaining bytes for each variant.

## Test Signals

Test byte-level encoding for every oplock and lease variant, unsolicited notification correlation, message-id based break type detection, request acknowledgement parsing, lease key and state offsets, malformed struct sizes, and integration with create lease contexts and cache-downgrade callbacks.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libsmb2/lib/smb2-cmd-oplock-break.c -->
