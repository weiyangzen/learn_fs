# sources/user-network-fs/impacket/impacket/krb5/constants.py

Purpose: centralizes Kerberos and MS-KILE numeric constants as `Enum` classes and helper maps. It is the numeric contract used by ASN.1 schemas, crypto selection, KDC requests, GSS flags, PAC signing, and error rendering.

Important APIs/types: `encodeFlags(flags)` returns a 32-element bit list for pyasn1 bit strings. Enums cover application tags, principal/name types, preauthentication data types, address types, authorization data, transited encoding, protocol version, message types, error codes, ticket flags, KDC options, AP options, PAC options, encryption types, and checksum types. `ERROR_MESSAGES` maps Kerberos error numbers to short and descriptive strings.

Control flow and state: pure constants plus `encodeFlags()`. No persistence or I/O.

Dependencies and integration: imports Impacket's DCE/RPC `Enum`. `asn1.py` uses application tag/message constants, `kerberosv5.py` uses options, enctypes, preauth types, and errors, `crypto.py` maps encryption/checksum IDs, and `pac.py` uses checksum IDs and non-Kerberos checksum salts.

Risks and test signals: numeric mistakes silently produce non-interoperable tickets or misleading errors. `encodeFlags()` does not bounds-check flag indexes; invalid indexes raise list errors. Tests should assert important enum values, `encodeFlags()` bit positions, and `KerberosError` rendering for generic NT-status e-data and superseded-user e-data.
