# sources/user-network-fs/impacket/impacket/krb5/asn1.py

Purpose: defines Kerberos ASN.1 structures for RFC 4120 and selected MS-KILE extensions using `pyasn1`. It is the schema layer used by ticket acquisition, cache conversion, GSS, password change, and PAC-related code to encode and decode DER/BER Kerberos messages.

Important APIs: helper builders `_application_tag()`, `_sequence_component()`, `_sequence_optional_component()`, `_vno_component()`, and `_msg_type_component()` centralize explicit/context/application tagging and protocol-version/message-type constraints. Mutation helpers `seq_set()`, `seq_set_dict()`, `seq_set_iter()`, `seq_set_flags()`, and `seq_append()` reduce boilerplate for nested pyasn1 sequences.

Important types: primitive wrappers include `Int32`, `UInt32`, `Microseconds`, `KerberosString`, `Realm`, `PrincipalName`, `KerberosTime`, `HostAddress`, `AuthorizationData`, `PA_DATA`, `KerberosFlags`, `EncryptedData`, `EncryptionKey`, and `Checksum`. Protocol structures include `Ticket`, `EncTicketPart`, `KDC_REQ_BODY`, `AS_REQ`, `TGS_REQ`, `AS_REP`, `TGS_REP`, `Authenticator`, `AP_REQ`, `AP_REP`, `KRB_SAFE`, `KRB_PRIV`, `KRB_CRED`, `KRB_ERROR`, preauth structures (`PA_ENC_TS_ENC`, `ETYPE_INFO`, `ETYPE_INFO2`), S4U/PAC option structures, key-list structures, superseded-user data, and DMSA key package data.

Control flow and state: this module is declarative. Runtime behavior occurs when other modules instantiate these classes and pyasn1 enforces tags, optional fields, and constraints. There is no persistence or mutable global state beyond class definitions.

Dependencies and integration: depends on `pyasn1.type` and `impacket.krb5.constants`. `kerberosv5.py` constructs AS/TGS/AP messages from these schemas; `ccache.py` decodes AS/TGS/KRB_CRED; `kpasswd.py` extends and uses several structures; `types.py` converts between Python wrappers and ASN.1.

Risks and test signals: schema drift is high impact because tag or field order mistakes break interoperability. `UInt32` intentionally lacks the commented range constraint. `KerberosString` accepts liberal UTF-8 rather than a strict alphabet. Tests should round-trip representative AS_REQ, TGS_REQ, AP_REQ, KRB_CRED, KRB_ERROR, S4U, and PAC option encodings and check optional-field omission paths.
