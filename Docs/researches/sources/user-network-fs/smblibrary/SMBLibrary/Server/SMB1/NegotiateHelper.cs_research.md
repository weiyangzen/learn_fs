# sources/user-network-fs/smblibrary/SMBLibrary/Server/SMB1/NegotiateHelper.cs

## Purpose

Builds SMB1 negotiate responses for classic and extended-security negotiation.

## Important APIs, Types, And Functions

`GetNegotiateResponse` returns a non-extended NTLM challenge response. `GetNegotiateResponseExtended` returns capability and GUID information for extended security. `CreateNegotiateMessage` builds the NTLM negotiate flags used for challenge generation.

## Control Flow

The classic path selects the NT LAN Manager dialect index, advertises server limits/capabilities, asks `GSSProvider` for an NTLM challenge, and stores the authentication context in connection state. Extended response advertises extended security and server GUID but does not include the token here.

## State And Persistence Behavior

Initializes connection authentication context and negotiated capability data; no filesystem state.

## Dependencies And Integration Points

Depends on SMB1 negotiate structures, `GSSProvider`, NTLM structures, and `SMBServer.NTLanManagerDialect`.

## Risks And Edge Cases

Dialect index is taken directly from `IndexOf`; absent dialect could become `0xFFFF` after cast. Capabilities are static and may advertise features only partially implemented. Time zone uses obsolete local time APIs.

## Test Signals

Test dialect selection, absent dialect behavior, capability flags, challenge generation, server time fields, and extended-security GUID response.

Source-read signal: reviewed the complete local source file for this item.
