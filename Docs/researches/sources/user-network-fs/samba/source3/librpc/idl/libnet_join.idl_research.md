# sources/user-network-fs/samba/source3/librpc/idl/libnet_join.idl

## Purpose
`libnet_join.idl` defines C-only libnet join and unjoin context calls. The declarations describe the large parameter/result surfaces for joining or leaving an AD/domain, including offline-domain-join support.

## Important APIs, types, and functions
- `libnetjoin_JoinDomNameType` classifies domain name input as unknown, DNS, or NetBIOS.
- `libnet_JoinCtx()` accepts DC/machine/domain/OU information, admin credentials, secret machine passwords, join flags, OS metadata, UPN/DNS host settings, ADS state, secure channel type, encryption type preferences, and offline-join controls. It returns account/domain/forest names, DN, GUID/SID, config modification status, errors, AD status, encryption type results, Kerberos salt, DC info, and RID.
- `libnet_UnjoinCtx()` describes unjoin inputs and outputs including account deletion/disable flags.

## Control flow
The IDL marks both calls `nopush,nopull,noopnum`, so it is a generated declaration surface for hand-written libnet logic rather than a network RPC contract. Implementations consume inputs, contact ADS/netlogon/SAMR as needed, update local config when requested, and populate outputs.

## State and persistence behavior
Join/unjoin operations can persistently alter Samba configuration, secrets, machine account passwords, Kerberos material, and domain membership state. Parameters marked `NDR_SECRET` prevent password disclosure in generated diagnostics. `ODJ_PROVISION_DATA` carries offline-join state.

## Dependencies and integration points
Imports include wkssvc flags, security, misc, netlogon, offline domain join data, and ADS structs. This interface bridges libnetapi join calls, ADS LDAP state, netlogon secure channel setup, and secrets storage.

## Risks and edge cases
The function surfaces contain secret strings and mutable config flags. Partial join/unjoin failures can leave local config, secrets, and remote machine accounts inconsistent. Offline provisioning and encryption type negotiation need careful compatibility handling. `ads_struct *` is unique and optional, so implementations must handle both preconnected and self-discovered ADS flows.

## Test signals
Test online join, unjoin with/without account deletion, precreated accounts, offline provisioning/request paths, DNS and NetBIOS domain names, UPN/SPN creation flags, encryption type setting, config modification rollback behavior, and secret redaction.
