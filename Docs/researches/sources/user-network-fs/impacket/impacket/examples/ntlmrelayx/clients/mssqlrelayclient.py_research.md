# sources/user-network-fs/impacket/impacket/examples/ntlmrelayx/clients/mssqlrelayclient.py

## Purpose
`mssqlrelayclient.py` provides an MSSQL/TDS relay target client. It wraps Impacket's `MSSQL` class to send NTLMSSP data inside TDS login and SSPI packets, enabling relay to SQL Server integrated authentication.

## Important APIs, Types, and Functions
`MYMSSQL` extends `MSSQL` with `initConnection()`, `sendNegotiate()`, `sendAuth()`, and `close()`. `MSSQLRelayClient` delegates relay calls to `MYMSSQL` and exposes helper methods `sql_query()`, `printReplies()`, and `printRows()` for attack modules.

## Control Flow
`MYMSSQL.initConnection()` connects and negotiates encryption. `sendNegotiate()` builds a TDS LOGIN7 packet with random host/app names, integrated-security flags, and the NTLM type 1 blob in `SSPI`, then reads the target's TDS SSPI response and parses the NTLM challenge from `Data[3:]`. `sendAuth()` unwraps SPNEGO, sends a TDS SSPI packet with type 3 data, parses replies, and treats `TDS_LOGINACK_TOKEN` as success.

## State and Persistence Behavior
`MYMSSQL` records `resp`, `sessionData['NTLM_CHALLENGE']`, and `sessionData['AUTH_ANSWER']`. `MSSQLRelayClient.sendAuth()` exposes that sessionData to the server/attack layer. SQL connection state remains in the underlying socket/TDS session.

## Dependencies and Integration Points
It depends on Impacket TDS constants and `MSSQL`, NTLM challenge parsing, SPNEGO, and ntlmrelayx `ProtocolClient`. Attack modules can execute SQL through `sql_query()`.

## Risks and Edge Cases
TDS encryption behavior is nuanced: when encryption is off, only the first login packet should remain TLS-wrapped, while TDS 8.0 keeps TLS. Failure detection depends on login-ack tokens and may miss useful error state. SQL authentication is explicitly not handled.

## Test Signals
Test SQL Server versions with encryption off/on/required, TDS 8.0, NTLM challenge parsing, SPNEGO type 3 unwrap, login failure token paths, and post-auth batch query execution.
