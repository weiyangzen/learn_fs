# sources/user-network-fs/impacket/impacket/krb5/ccache.py

Purpose: implements MIT Kerberos credential cache parsing/serialization plus conversion between ccache credentials, Impacket TGT/TGS dictionaries, and kirbi/KRB_CRED blobs. It lets tools reuse tickets from `KRB5CCNAME`, save new tickets, and convert ticket formats.

Important APIs/types: binary `Structure` classes model headers, counted strings, key blocks, times, addresses, authdata, principals, and credentials. `Principal` converts between cache principals and `types.Principal`. `Credential` parses a single credential and exposes `toTGT()`/`toTGS()`. `CCache` parses complete caches, serializes via `getData()`/`saveFile()`, finds credentials with `getCredential()`, imports AS/TGS replies with `fromTGT()`/`fromTGS()`, reads environment caches with `parseFile()`, and converts kirbi files using `fromKRBCRED()`/`toKRBCRED()`.

Control flow and persistence: `CCache.__init__()` detects file version, parses v4 headers, primary principal, then credentials while skipping `krb5_ccache_conf_data`. `fromTGT()` and `fromTGS()` decrypt reply encrypted parts using key usages 3 and 8, derive credential metadata and ticket blobs, and append credentials. `parseFile()` reads `KRB5CCNAME`, searches for a requested SPN, then falls back to a krbtgt principal. File persistence is direct read/write of binary ccache or kirbi data.

Dependencies and integration: uses `pyasn1` DER codecs, Kerberos ASN.1 schemas, `crypto`, `constants`, `types`, and Impacket logging. `kerberosv5.py`, `ldap.py`, and `kpasswd.py` use it for cache-based authentication.

Risks and test signals: malformed caches can break offset arithmetic because parsing trusts embedded lengths. `getCredential(anySPN=True)` has complex SPN normalization including host-only S4U cases and should be tested with ports, case, service changes, and machine-account names. `reverseFlags()` normalizes pyasn1 bit strings to 32 bits. Time conversion mixes naive epoch timestamps with UTC-aware kirbi output. Tests should round-trip ccache v3/v4, AS/TGS imports, KRB_CRED conversion, missing `renew-till`, absent `KRB5CCNAME`, and malformed counted strings.
