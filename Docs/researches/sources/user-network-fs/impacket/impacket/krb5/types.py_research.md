# sources/user-network-fs/impacket/impacket/krb5/types.py

Purpose: supplies Python-friendly Kerberos wrapper types and conversions around ASN.1 structures: principals, addresses, encrypted data, tickets, and Kerberos time.

Important APIs/types: `_asn1_decode()` decodes pyasn1 data and rejects trailing substrate. `Principal` parses strings with escapes and realms, tuples/lists, or copies existing principals; it can convert from ASN.1 and write name components to ASN.1. `Address` is a partial address wrapper. `EncryptedData` converts ASN.1 encrypted data to Python fields and back. `Ticket` converts ASN.1 tickets to service principal/encrypted-part fields and back. `KerberosTime` formats/parses UTC generalized time.

Control flow and state: objects hold in-memory fields only. Principal parsing handles quoted `/`, `@`, and backslash characters, defaults realm when absent, and treats unknown name types as wildcard-compatible in equality. Ticket and encrypted-data wrappers delegate schema details to `asn1.py`.

Dependencies and integration: uses stdlib `datetime`, `socket`, `re`, `struct`, pyasn1 DER decoder, `six.ensure_binary`, and local `asn1/constants`. These wrappers are used across `kerberosv5.py`, `ccache.py`, and `kpasswd.py`.

Risks and test signals: `Address.family` and `Address.address` check IPv4 in both branches, so IPv6 appears unreachable. `Address.encode()` is unimplemented. `Principal.__eq__()` uses `all(map(...))`, which can ignore length mismatches after matching prefix. `EncryptedData.from_asn1()` uses `str()` for ciphertext, which may be risky for bytes-like octets. Tests should cover escaped principal parsing, tuple forms, wildcard type equality, unequal component lengths, ASN.1 ticket round-trips, strict trailing DER rejection, KerberosTime non-Z rejection, and IPv6 address behavior.
