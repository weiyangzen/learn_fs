# sources/user-network-fs/impacket/impacket/tds.py

## Purpose

`tds.py` implements Impacket's SQL Server Discovery Protocol (`MC-SQLR`) and Tabular Data Stream (`MS-TDS`) client support. It can discover SQL instances over UDP 1434, connect to SQL Server over TCP, negotiate prelogin encryption, authenticate with SQL auth, NTLM, or Kerberos, send SQL batches, parse server tokens, decode selected SQL row types, and print query results.

## Important APIs, Types, And Functions

The SQL Browser surface is `SQLR`, `SQLR_UCAST_INST`, `SQLR_UCAST_DAC`, `SQLR_Response`, and `MSSQL.getInstances()`. The TDS packet surface includes packet type, encryption, token, environment-change, column-type, LOGIN7-version, and TDS 8.0 all-headers constants. `TDSPacket`, `TDS_PRELOGIN`, `TDS_LOGIN`, `TDS_LOGIN_ACK`, `TDS_FEATUREEXTACK`, `TDS_INFO_ERROR`, `TDS_INFO_ERROR72`, `TDS_ENVCHANGE`, `TDS_DONE*`, `TDS_COLMETADATA`, `TDS_ROW`, and `TDS_SSVARIANT` model protocol records.

The central class is `MSSQL`. Its workflow APIs include `connect()`, `disconnect()`, `preLogin()`, `login()`, `kerberosLogin()`, `sendTDS()`, `recvTDS()`, `parseReply()`, `batch()`, `batchStatement()`, `sql_query`, `changeDB()`, `RunSQLQuery()`, and `RunSQLStatement()`. TLS helpers include `set_tls_context()`, `_setup_tds8()`, `tls_send()`, and `tls_recv()`. Row/token helpers include `generate_cbt_from_tls_unique()`, `parseColMetaData()`, `parseRow()`, `_parse_reply_tokens()`, `processColMeta()`, and result printing methods.

## Control Flow

`connect()` opens a TCP socket and resets TLS/session state. `_negotiate_encryption()` sends `TDS_PRELOGIN`, parses the server encryption byte, retries as TDS 8.0 if a plain prelogin is reset or if `TDS_ENCRYPT_STRICT` is returned, and otherwise establishes login-scoped in-memory TLS when the server supports or requires encryption. `login()` builds LOGIN7 fields, chooses SQL credentials or NTLM SSPI, sends the login packet, disables TLS after the first packet when encryption is only login-scoped, handles NTLM challenge/response plus MIC/channel binding when needed, and accepts success on LOGINACK. `kerberosLogin()` obtains cached or fresh tickets, builds SPNEGO/AP-REQ data, optionally embeds channel binding, sends it in `SSPI`, and parses the result.

`sendTDS()` fragments large payloads by packet size; `recvTDS()` reassembles packets until `TDS_STATUS_EOM`. TLS-over-TDS uses `ssl.MemoryBIO` and embeds handshake bytes in prelogin packets, while TDS 8.0 wraps the TCP socket directly in TLS and prepends all-headers data to SQL batches. Query execution clears result state, sends UTF-16LE SQL text, parses token streams, updates `packetSize`, `currentDB`, `colMeta`, `rows`, `replies`, and `lastError`, then returns decoded rows or raises stored SQL errors through high-level methods.

## State And Persistence Behavior

The module persists nothing locally. `MSSQL` maintains socket and TLS objects, receive buffer, packet size, login version, current database, server version, accumulated replies, column metadata, decoded rows, and last error. Remote state may change because callers can execute arbitrary SQL through `batch()` and `RunSQLStatement()`.

## Dependencies And Integration Points

It depends on Python socket/select/ssl/date/decimal/struct utilities, Impacket `ntlm`, `uuid`, `LOG`, `Structure`, and `impacket.mssql.version.MSSQL_VERSION`. Kerberos paths import SPNEGO, ccache, ASN.1, Kerberos crypto, constants, and `pyasn1` lazily. The module underpins Impacket MSSQL tools that need instance discovery, authentication, query execution, EPA/channel binding, and token/row parsing.

## Risks And Edge Cases

TLS certificate verification is disabled, which is useful for tooling but allows MITM. Channel binding relies on `tls-unique`; TLS 1.3 is intentionally capped out for TDS 8.0. LOGIN7 layout and token parsing depend on correct session version state. Row decoding supports only selected SQL types and raises on unknown types. Some comparisons use `is` for small integer token values, and numeric parsing changes global decimal precision. `RunSQLQuery()` checks `lastError` twice. SQL execution is inherently high-impact on remote servers.

## Test Signals

Tests should cover prelogin encryption responses, strict TDS 8.0 retry, LOGIN7 legacy versus 7.4 serialization, FEATUREEXTACK parsing, NTLM MIC/channel binding, Kerberos CBT checksum generation, packet fragmentation/reassembly, TDS 8.0 SQL batch headers, metadata user-type width, and row decoding for nullable strings, GUID, numeric, date/time, money, and sql_variant values. Integration tests require SQL Server fixtures for SQL auth, NTLM, Kerberos, and strict encryption.
