# sources/user-network-fs/samba/source4/libnet/libnet_lookup.h

## Purpose
`libnet_lookup.h` declares libnet data structures for host lookup, DC lookup, and name-to-SID lookup.

## Important APIs, Types, And Functions
`struct libnet_Lookup` takes hostname, NBT name type, and optional resolve context, returning address list. `struct libnet_LookupDCs` takes domain name and name type, returning DC count and `nbt_dc_name` array. `struct libnet_LookupName` takes account/group name plus domain name, returning SID pointer, RID, LSA SID type, SID string, and error string. `struct msg_net_lookup_dc` is a monitor payload for DC lookup messages.

## Control Flow
The structures correspond to `libnet_lookup.c`: generic hostname resolution, host shortcut resolution, CLDAP DC discovery, and LSA name lookup. `LookupName` callers should provide a domain name suitable for opening an LSA policy handle.

## State And Persistence Behavior
The header has no persistence behavior. Its outputs are read-only lookup results allocated by implementation receive functions.

## Dependencies And Integration Points
The declarations reference resolve contexts, NBT DC-name structures, SID types, and LSA SID type enums. They integrate with group/user/domain code that needs name resolution before SAMR operations.

## Risks
The address and DC outputs are pointer-based and depend on caller memory context lifetime. The plural DC lookup structure may contain only one DC from the current implementation. SID output may be null when no name match is found even if the wrapper reports a successful completed lookup.

## Test Signals
API tests should validate struct initialization and output ownership. Functional tests should cover hostname resolution, DC discovery, name lookup success and no-match behavior, and monitor payload correctness when used by callers.
