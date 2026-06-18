# sources/user-network-fs/samba/source4/libcli/dgram/mailslot.c

Purpose: implements Class 2 NetBIOS datagram mailslots, the SMB transaction-in-datagram mechanism used for small browse and Netlogon mailslot messages.

Important APIs: `dgram_mailslot_listen()` registers a handler; `dgram_mailslot_find()` locates one by case-insensitive name; `dgram_mailslot_name()` validates and extracts a mailslot name from a datagram; `dgram_mailslot_temp()` creates a randomized temporary reply slot; `dgram_mailslot_send()` builds an NBT datagram with SMB transaction body; `dgram_mailslot_data()` returns the payload slice.

Control flow: listen allocates a handler, links it into `dgmsock->mailslot_handlers`, installs a destructor to unlink it, and enables fd reads. Send builds `nbt_dgram_packet` fields, gets the local socket address, fills `dgram_message` and `smb_trans_body`, then queues it through `nbt_dgram_send()`. Data extraction adjusts for padding based on `data_offset`.

State and persistence: handler registration is persistent only for the lifetime of the talloc object. Temporary mailslot creation tries up to 100 random suffixes. No disk state exists.

Dependencies and integration: depends on tevent, dlink lists, socket address helpers, and the NBT datagram structures. It is used by browse and netlogon datagram helpers.

Risks: comments note Class 1 mailslots and 425/426-byte edge sizes are unsupported. `msg->length` and `data_offset` calculations are described as crude, so wire-compatibility edge cases deserve coverage. Temporary slot random collisions are bounded but possible. Test signals include malformed padding in `dgram_mailslot_data()`, unsupported datagram body types, broadcast/direct message types, and large message behavior near the documented class boundary.
