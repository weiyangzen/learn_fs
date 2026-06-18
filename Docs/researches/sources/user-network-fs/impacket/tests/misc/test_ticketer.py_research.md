# sources/user-network-fs/impacket/tests/misc/test_ticketer.py

Purpose: Tests `examples.ticketer.TICKETER` ticket-time extraction and reuse for requested Kerberos tickets.

Important APIs, types, and functions: Uses `TICKETER`, `EncASRepPart`, `EncTGSRepPart`, `EncTicketPart`, `EncryptionTypes`, `PrincipalNameType`, `TicketFlags`, `encodeFlags`, `KerberosTime`, pyasn1 `encoder`, `noValue`, `mock.patch`, and `SimpleNamespace` options.

Control flow: Helpers build synthetic options and DER-encoded AS/TGS reply parts with fixed timestamps. Tests patch `_enctype_table` with fake ciphers to assert key usage, verify fallback handling for missing optional times, mock `getKerberosTGT` and decoder wiring, then seed requested times and validate `customizeTicket` applies them to both encrypted reply and ticket parts.

State and persistence behavior: In-memory ASN.1 structures. `TICKETER` stores requested times in private `__requested_ticket_times`.

Dependencies and integration points: Integrates ticket generation example code with Kerberos ASN.1, crypto table dispatch, and KDC-request reuse behavior.

Risks: Private attribute assertions are coupled to implementation internals. Timestamp handling is sensitive to optional ASN.1 fields and AS/TGS key-usage differences.

Test signals: Strong signal for reply decryption key usage, time extraction, optional time fallbacks, request wiring, and requested-lifetime reuse.
