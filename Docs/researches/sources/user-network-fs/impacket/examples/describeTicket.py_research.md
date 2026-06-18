# sources/user-network-fs/impacket/examples/describeTicket.py

## Purpose
`describeTicket.py` parses Kerberos ccache credentials, prints visible ticket metadata, optionally emits Kerberoast-compatible hashes, decrypts ticket encrypted parts when service keys are supplied, and decodes PAC structures including logon info, UPN/DNS, checksums, delegation, requestor, attributes, and PAC credentials.

## Important APIs, Types, and Functions
`parse_ccache()` loads `CCache`, converts each credential to TGS form, decodes `TGS_REP`, prints times, flags, key types, and selects/generates decryption keys through `generate_kerberos_keys()`. It decrypts the ticket enc-part with `_enctype_table` and parses `EncTicketPart`, `AD_IF_RELEVANT`, and `pac.PACTYPE`.

`parse_pac()` walks PAC buffers and uses Impacket PAC structures such as `KERB_VALIDATION_INFO`, `PAC_CLIENT_INFO`, `UPN_DNS_INFO`, `PAC_SIGNATURE_DATA`, `PAC_CREDENTIAL_INFO`, `S4U_DELEGATION_INFO`, `PAC_ATTRIBUTE_INFO`, and `PAC_REQUESTOR`. Helper enums decode user flags, group attributes, UAC flags, and PAC flags. `kerberoast_from_ccache()` formats RC4, AES, and DES service-ticket hashes. `parse_args()` validates salt/user/domain combinations for key derivation and accepts `--asrep-key` for PAC credential decryption.

## Control Flow
The CLI validates arguments and calls `parse_ccache()`. For each credential, the script prints unencrypted cache and ticket metadata, attempts Kerberoast hash generation for non-krbtgt tickets, then tries to derive or load the key matching the ticket encryption type. If no matching key exists, it logs and moves to the next credential. If decryption succeeds, it parses authorization data as PAC and logs each decoded PAC section in a structured format.

## State and Persistence
The script is read-only with respect to its input ticket file and does not create output files. It can print sensitive session keys, cache keys, service-ticket hashes, PAC hashes from UnPAC-the-Hash, and account metadata to stdout/logging. State is local to parsed credentials and derived key dictionaries.

## Dependencies and Integration Points
Dependencies include PyCryptodome MD4, pyasn1 DER decoding, Impacket Kerberos ASN.1, crypto, PAC, CCache, DCE/RPC type serialization, LDAP SID formatting, and example logging. It integrates with offline `.ccache` files and Kerberos key material supplied by CLI arguments.

## Risks
Output can disclose reusable secrets and crackable hashes. PAC parsing assumes expected buffer forms and can fail on unsupported or malformed PAC data. `kerberoast_from_ccache()` has a dead `raise` before debug logging in its exception block. The AES128 formatting branch appears to use `.decode` without calling it, which should be tested. Decrypting PAC credentials with `--asrep-key` exposes LM/NT material.

## Test Signals
Test with ccaches containing TGTs, RC4 service tickets, AES service tickets with correct and incorrect salts, expired tickets, missing kvno, PAC-less tickets, and PACs containing extra SIDs, delegation, requestor, and credentials info. Unit tests can target FILETIME conversion, flag decoding, Kerberoast hash formatting, and argument validation.
