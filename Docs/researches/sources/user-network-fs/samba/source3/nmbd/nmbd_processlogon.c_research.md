# sources/user-network-fs/samba/source3/nmbd/nmbd_processlogon.c

## Purpose
`nmbd_processlogon.c` handles domain logon and domain-controller discovery datagrams received on the NETLOGON mailslots. It decodes NBT netlogon requests, builds legacy or NT4-style response structures, and sends them back as NetBIOS datagram mailslot replies when this Samba instance is acting as a domain controller.

## Important APIs, types, and functions
- `process_logon_packet` is the exported entry point called from the datagram packet dispatcher.
- `delay_logon` checks delayed-host configuration against client name/address.
- `delayed_init_logon_handler` requeues a locked packet after a `tevent` timer expires.
- Generated NDR helpers marshal and unmarshal `nbt_netlogon_packet` and `nbt_netlogon_response`.

## Control flow
The handler finds the outgoing interface for the peer, rejects requests when domain logons are disabled, decodes the source NetBIOS name, unmarshals the NDR request, then switches on command. It answers `LOGON_REQUEST`, answers `LOGON_PRIMARY_QUERY` only for a domain master, and answers `LOGON_SAM_LOGON_REQUEST` with optional delayed handling for empty-user initial logons.

## State and persistence behavior
No disk state is persisted. The only long-lived state is delayed packet ownership: the packet is marked `locked`, retained by a timer, then requeued for processing. Response content is generated from runtime configuration such as NetBIOS name, workgroup, and domain-master mode.

## Dependencies and integration points
This file integrates with `send_mailslot`, `queue_packet`, `nmbd_event_context`, Samba loadparm accessors, interface lookup helpers, generated netlogon NDR code, and datagram mailslot dispatch in `nmbd_packets.c`.

## Risks and edge cases
Delayed packets require balanced lock/unlock behavior. The path is IPv4-interface dependent and returns if no outgoing interface is found. Empty usernames drive delay policy, so client discovery timing depends on configuration and request shape.

## Test signals
Tests should send NBT netlogon mailslot packets for `LOGON_REQUEST`, `LOGON_PRIMARY_QUERY`, and `LOGON_SAM_LOGON_REQUEST`, with DC/domain-master and delay settings varied, and assert response fields plus requeue behavior.
