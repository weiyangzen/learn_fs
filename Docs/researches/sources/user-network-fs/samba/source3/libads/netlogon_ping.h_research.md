# sources/user-network-fs/samba/source3/libads/netlogon_ping.h

## Purpose

`netlogon_ping.h` declares the ADS NetLogon ping API and filter structure used to discover domain controllers over CLDAP/LDAP-family transports.

## Important APIs, Types, and Functions

`struct netlogon_ping_filter` contains `ntversion`, domain, domain SID, domain GUID, hostname, user, account-control filter, and required DC flags. The header declares `check_cldap_reply_required_flags`, async `netlogon_pings_send`, `netlogon_pings_recv`, and synchronous `netlogon_pings`.

## Control Flow

Callers provide a protocol, server address array, filter, wanted response count, and timeout. Async callers drive the returned `tevent_req`; synchronous callers use `netlogon_pings`, which creates an event context and polls the request to completion.

## State and Persistence Behavior

The header defines request contracts only. Returned `netlogon_samlogon_response` arrays are talloc-moved to the caller and contain per-server response slots.

## Dependencies and Integration Points

It depends on tsocket address types, generated NBT/NetLogon declarations, NTSTATUS, and loadparm's `client_netlogon_ping_protocol` enum. It integrates directly with ADS DC discovery in `ldap.c`.

## Risks and Test Signals

Risks include callers passing mismatched signed `int` counts to size_t implementations, unclear ownership of the server array versus returned response array, and timeout semantics needing validation against implementation. Tests should compile async and sync callers, verify filter defaults such as `acct_ctrl = -1`, and assert response ownership on success/failure.
