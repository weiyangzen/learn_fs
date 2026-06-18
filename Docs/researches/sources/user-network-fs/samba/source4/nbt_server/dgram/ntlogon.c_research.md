# sources/user-network-fs/samba/source4/nbt_server/dgram/ntlogon.c

## Purpose

`dgram/ntlogon.c` is a legacy NTLOGON mailslot handler that parses NTLOGON packets and can answer simple SAM logon requests with an NT4-style reply.

## Important APIs, Types, and Functions

The exported callback is `nbtd_mailslot_ntlogon_handler()`. The internal responder `nbtd_ntlogon_sam_logon()` builds `struct nbt_ntlogon_packet` replies. It uses `dgram_mailslot_ntlogon_parse()`, `dgram_mailslot_ntlogon_reply()`, `nbtd_find_iname()`, and `nbtd_find_reply_iface()`.

## Control Flow

The handler verifies the destination NetBIOS name is locally registered, parses the NTLOGON packet, logs it, and dispatches on command. For `NTLOGON_SAM_LOGON`, the responder only answers PDC or LOGON destination names, fills server/user/domain/version/token fields, clears destination name type to zero, and sends the reply to the request's mailslot.

## State and Persistence Behavior

No persistent state is written. The function reads the registered-name list and loadparm NetBIOS/workgroup settings. Reply packet fields borrow some strings from the incoming packet context.

## Dependencies and Integration Points

Dependencies include NBT datagram mailslot helpers, generated NBT NTLOGON structs, service task loadparm access, and interface selection. Note that `dgram/request.c` currently maps `NBT_MAILSLOT_NTLOGON` to the Netlogon handler, so this file may be legacy or used by other registrations outside this snippet.

## Risks and Test Signals

Risks include bitrot if the handler is not registered, lack of server-role/domain checks in the legacy reply path, and clearing destination name type in the input packet before reply. Tests should confirm whether this handler is reachable, parse valid/invalid NTLOGON packets, and verify SAM_LOGON replies only for PDC/LOGON names.
