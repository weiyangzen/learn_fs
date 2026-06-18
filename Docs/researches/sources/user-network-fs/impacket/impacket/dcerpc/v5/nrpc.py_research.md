# sources/user-network-fs/impacket/impacket/dcerpc/v5/nrpc.py

## Purpose

`nrpc.py` implements much of the MS-NRPC Netlogon Remote Protocol interface. It combines a large IDL mapping for domain controller discovery, secure-channel authentication, logon validation, replication deltas, trusts, control calls, and UAS compatibility calls with helper cryptographic routines for Netlogon credentials, authenticators, signing, sealing, and SSP type-1 messages.

## Important APIs, Types, and Functions

`MSRPC_UUID_NRPC` identifies the Netlogon interface. `DCERPCSessionError` formats errors from both `system_errors` and `nt_errors`. Constants cover DNS name types, OS suite/product flags, Netlogon access masks, control function codes, SSP message flags, signature algorithms, and seal algorithms. Core secure-channel types include `NETLOGON_CREDENTIAL`, `NETLOGON_AUTHENTICATOR`, `NETLOGON_SECURE_CHANNEL_TYPE`, `NL_TRUST_PASSWORD`, `NETLOGON_CAPABILITIES`, and password/hash structures. Discovery/trust types include `DOMAIN_CONTROLLER_INFOW`, site-name arrays, socket/DNS records, `DS_DOMAIN_TRUSTSW`, and forest-trust pointers from LSAD. Logon types include `NETLOGON_LOGON_IDENTITY_INFO`, `NETLOGON_LEVEL`, logon info classes, validation unions, SAM validation structures, groups, extra SIDs, and session keys. Replication support includes many `NETLOGON_DELTA_*` structures, delta ID/union mappings, sync state, and delta arrays. Control and UAS structures model the older management calls.

Cryptographic helpers include `ComputeNetlogonCredential`, `ComputeNetlogonCredentialAES`, `ComputeSessionKeyAES`, `ComputeSessionKeyStrongKey`, authenticator generation, sequence-number derivation/encryption, MD5/SHA256 signatures, `SIGN`, `SEAL`, `UNSEAL`, `CompressedUtf8String`, and `getSSPType1`. RPC classes cover opnums 0 through 49 with gaps, and `OPNUMS` registers implemented calls. Helper request builders cover challenge/authenticate, DC discovery, password get/set, domain info, capabilities, and trust info.

## Control Flow

Typical secure-channel setup starts with `hNetrServerReqChallenge`, derives a session key from shared secret and challenges, computes a client credential, and calls one of the authenticate helpers. Later authenticated calls pass `NETLOGON_AUTHENTICATOR` values generated from the stored credential and session key. Signing and sealing compute Netlogon auth signatures over message bytes, confounders, sequence numbers, and session keys, with RC4/HMAC-MD5 or AES/HMAC-SHA256 depending on the `aes` flag. RPC helpers normalize many string parameters through `checkNullString`, assign enum/union tags where needed, seed zero return authenticators when omitted, and call `dce.request`.

## State and Persistence Behavior

The module itself has no durable local state, but helper crypto functions are stateful through caller-managed session keys, credentials, timestamps, sequence numbers, and authenticators. Remote operations can query or affect domain-controller discovery, secure-channel password material, DNS records, Netlogon service bits, SAM/logon validation, replication cursors, and trust information. `ComputeNetlogonAuthenticator*` uses current wall-clock time for timestamps.

## Dependencies and Integration Points

It depends on `time`, `struct`, `six`, `hmac`, `hashlib`, `Cryptodome.Cipher` DES/AES/ARC4, Impacket NDR and dtypes, `samr`, `lsad`, `rpcrt`, `Structure`, `ntlm`, `crypto`, and logging. It integrates with LSAD for forest trust structures, SAMR for logon-hour and integer types, and DCE/RPC transport bindings to the Netlogon UUID. Higher-level Impacket tools use this module for machine-account authentication, domain discovery, trust enumeration, and Netlogon signing/sealing.

## Risks and Edge Cases

If `pycryptodomex` is missing, import only logs critical messages; later crypto calls can fail with missing DES/AES/ARC4 names. `checkNullString` assumes string-like values and appends `'\x00'`, which can be fragile for bytes versus str callers. Crypto correctness is sensitive to negotiated flags, challenge order, sequence numbers, confounder presence, and AES versus RC4 mode. Some declared operations are intentionally omitted from `OPNUMS`, including password set opnum 6 and chain/client DNS update entries. Several structures contain dummy/reserved fields and duplicated class names, so layout regression is a risk. Netlogon operations are high-impact because they involve machine trust, password material, replication data, and authentication decisions.

## Test Signals

Tests should include known-vector coverage for session key derivation, DES/AES credentials, authenticator timestamps with controlled time, signing/sealing/unsealing round trips, compressed UTF-8 DNS labels, and SSP type-1 buffers. NDR tests should cover union tag selection for logon, validation, delta, control, workstation, and domain-information unions. Fake-DCE helper tests should assert string normalization and field population. Integration tests require an isolated domain controller and should cover challenge/authenticate, DC discovery, capabilities, and trust enumeration without altering production trust passwords.
