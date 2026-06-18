# sources/user-network-fs/impacket/examples/GetLAPSPassword.py

## Purpose

`GetLAPSPassword.py` extracts Microsoft LAPS and LAPSv2 passwords from Active Directory. It queries computer objects with legacy `ms-MCS-AdmPwd`, cleartext `msLAPS-Password`, or encrypted `msLAPS-EncryptedPassword`, decrypts LAPSv2 blobs through MS-GKDI when needed, and prints or writes a table of recovered passwords and expiration times.

## Important APIs, Types, and Functions

`GetLAPSPassword.printTable` formats console and optional tab-delimited file output. `__init__` stores credentials, Kerberos/hash options, target computer, LDAPS flag, output file, and a KDS cache. `getLAPSv2Decrypt` parses `EncryptedPasswordBlob`, CMS `EnvelopedData`, key identifiers, recipient info, obtains group key material with `GkdiGetKey`, derives KEK/CEK using `dpapi_ng`, and decrypts plaintext. `run` performs the LDAP search and result extraction.

## Control Flow

The CLI parses target identity, optional `-computer`, `-ldaps`, and output/authentication options. `run` logs into LDAP, builds a filter for computer objects with LAPS attributes, optionally restricts by name, and requests the relevant LAPS fields with a 1000-entry paged control. For each LDAP entry, it decodes the host name, decrypts LAPSv2 when `msLAPS-EncryptedPassword` is present, parses the decrypted JSON-like payload for username/password, handles expiration FILETIME fields, handles legacy `ms-MCS-AdmPwd`, accumulates rows, and prints the table.

## State and Persistence Behavior

The script reads LDAP attributes and, for encrypted LAPSv2, performs RPC calls to MS-GKDI. It caches `GroupKeyEnvelope` values by root key ID in memory. It may write recovered passwords to `-outputfile`. It does not modify AD state.

## Dependencies and Integration Points

It depends on Impacket LDAP, DCERPC transport/EPM/GKDI, DPAPI-NG helpers, pyasn1 CMS decoding, JSON parsing, and Active Directory LAPS/LAPSv2 schema. The `-ldaps` option is important for environments enforcing LDAP over SSL.

## Risks and Edge Cases

Recovered secrets are printed and optionally written in cleartext. `getLAPSv2Decrypt` can reference `key_id` or `laps_enabled` after parse exceptions, so malformed blobs can produce follow-on errors. GKDI cache assignment uses `gke['RootKeyId']`, which must match key identifier types. The decrypted plaintext is sliced with `[:-18]` before UTF-16LE JSON decoding, which assumes blob trailer shape. RPC auth level is set twice, ending at privacy. LDAP result processing catches per-entry errors and continues, which can hide systematic decryption failures.

## Test Signals

Unit tests should cover FILETIME conversion, table output, LAPSv2 blob parse/decrypt with known fixtures or mocks, GKDI cache hits, malformed blobs, legacy LAPS attribute extraction, and output file formatting. Integration tests require an AD/LAPS lab with permissions for both legacy and LAPSv2 reads.
