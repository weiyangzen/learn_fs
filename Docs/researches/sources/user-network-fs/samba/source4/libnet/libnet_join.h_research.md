# sources/user-network-fs/samba/source4/libnet/libnet_join.h

## Purpose
`libnet_join.h` declares the public data structures for domain join operations and local join secret storage inputs.

## Important APIs, Types, And Functions
`enum libnet_Join_level` and `enum libnet_JoinDomain_level` distinguish automatic discovery from specified parameters. `struct libnet_JoinDomain` includes domain/account/netbios/binding/level/account-type/recreate/password inputs and rich outputs including join password, domain SID/name/realm, domain/account/server DNs, KVNO, SAMR pipe/binding/user handle, account SID, and account GUID.

`struct libnet_Join_member` is a smaller workstation-member join request with domain, optional NetBIOS name, level, and optional password, returning join password/domain SID/domain name. `struct libnet_set_join_secrets` describes data needed to store local secrets: domain, realm, NetBIOS/account names, secure-channel type, password, KVNO, and domain SID.

## Control Flow
The header supports the two-layer implementation: `JoinDomain` handles remote account join and AD finishing, while `Join_member` wraps it and stores local secrets. The secret structure is compatible with provisioning storage logic.

## State And Persistence Behavior
The header itself has no persistence behavior. Its structures carry secret data (`join_password`, `account_pass`) and live RPC handles. Implementations can mutate remote domain accounts and local secrets databases based on these fields.

## Dependencies And Integration Points
The header includes generated netlogon declarations for `netr_SchannelType` and references Samba SID, GUID, DCE/RPC pipe, binding, and policy-handle types. It is used by join commands, provisioning paths, and tests.

## Risks
Callers must protect password fields and manage returned handle lifetimes. `recreate_account` signals potentially destructive remote account replacement. `acct_type` must match SAMR account-control expectations. Automatic vs specified levels determine whether binding or domain discovery is used.

## Test Signals
API tests should verify field propagation from `libnet_JoinDomain()` and `libnet_Join_member()`, including KVNO/account GUID for AD joins and local secret settings for member joins. Security-oriented tests should ensure password fields are not logged unexpectedly by callers.
