# sources/user-network-fs/samba/source3/librpc/idl/rpcd_witness.idl

## Purpose
`rpcd_witness.idl` defines persistent registration records and update messages for Samba's witness RPC daemon. Witness lets clients register for cluster/share move and failover notifications.

## Important APIs, types, and functions
- `rpcd_witness_registration` is the record stored in `rpcd_witness_registration.tdb`, including version, net/share names, IP/client names, flags, timeout, context handle, server ID, account/domain/SID, local/remote addresses, and registration time.
- `rpcd_witness_registration_update_type` enumerates client/share move targets, force unregister, and force response events.
- `rpcd_witness_registration_updateU` is a switch union for node/IPv4/IPv6 moves and forced response payloads.
- `rpcd_witness_registration_updateB` wraps a context handle, update type, and union payload for messages.

## Control flow
Registration records are stored when clients register. Later, internal witness update messages select a union arm by update type and drive notifications or unregister/response behavior for the matching context handle.

## State and persistence behavior
Registrations are persistent TDB records and contain identity, authorization, endpoint, and timeout metadata. Update messages are transient. IP address payloads are marked big-endian to preserve network byte order.

## Dependencies and integration points
The IDL imports misc, server ID, security, and witness protocol definitions. Generated code builds `NDR_RPCD_WITNESS` and is used by rpcd witness registration storage and messaging.

## Risks and edge cases
Stored registration schema compatibility matters for daemon restart/upgrade. Context-handle matching, timeout expiry, and account SID/domain validation are security-sensitive. Union cases with empty payloads must remain unambiguous. IPv4/IPv6 endian attributes must match network clients.

## Test signals
Test registration encode/decode, TDB reload, forced unregister, forced response, client and share moves to node/IPv4/IPv6, timeout expiry, and invalid switch values.
