# sources/user-network-fs/impacket/tests/misc/test_tds.py

Purpose: Tests TDS/MSSQL packet serialization, TDS 8 negotiation behavior, packet receive buffering, SQL batch wrapping, and MSSQL SOCKS relay TDS8 handling.

Important APIs, types, and functions: Uses `tds.TDSPacket`, `TDS_PRELOGIN`, `TDS_INFO_ERROR`, `TDS_INFO_ERROR72`, `TDS_LOGIN`, `MSSQL`, constants such as `TDS_PRE_LOGIN`, `TDS_TABULAR`, `TDS_ENCRYPT_STRICT`, and `MSSQLSocksRelay`.

Control flow: `TDSTests` builds packets and mocks MSSQL sockets/prelogin behavior to validate serialization, retry policy, TDS8 wrapping, partial reads, and buffered next-packet handling. `MSSQLSocksRelayTests` mocks relay sessions and sockets to validate strict encryption advertisement, TLS-first local clients, wrapping policy, and partial reads from local clients.

State and persistence behavior: Uses mocked sockets and in-memory buffers. `recvTDS` maintains buffered bytes across calls.

Dependencies and integration points: Integrates core `impacket.tds` with ntlmrelayx MSSQL SOCKS plugin behavior.

Risks: Packet reassembly and TDS8 negotiation are network-state-sensitive. Timeout vs connection-close retry behavior is intentionally distinct.

Test signals: Strong signal for TDS length fields, default login version, TDS8 retry/wrap logic, partial TLS reads, buffered packet preservation, strict encryption negotiation, and relay wrapping decisions.
