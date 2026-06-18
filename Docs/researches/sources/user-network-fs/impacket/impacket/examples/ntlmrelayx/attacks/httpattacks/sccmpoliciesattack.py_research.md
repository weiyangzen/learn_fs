# sources/user-network-fs/impacket/impacket/examples/ntlmrelayx/attacks/httpattacks/sccmpoliciesattack.py

## Purpose
`sccmpoliciesattack.py` implements an SCCM Management Point relay attack that registers a spoofed ConfigMgr client, requests machine policy assignments, identifies secret policies, decrypts them, deobfuscates secret blobs, and writes credentials/scripts/policy material to a loot directory.

## Important APIs, Types, and Functions
- XML templates define client registration, message headers, policy request bodies, and reporting payloads.
- Crypto helpers: `create_private_key()`, `create_certificate()`, `SCCM_sign()`, `build_MS_public_key_blob()`, `mscrypt_derive_key_sha1()`.
- Payload helpers: `encode_UTF16_strip_BOM()`, `clean_junk_in_XML()`, `generate_registration_request_payload()`, and `generate_policies_request_payload()`.
- Decryption helpers: `decrypt_key_OEAP()`, `decrypt_key_RSA()`, `decrypt_body_triple_DES()`, `decrypt_body_AESCBC()`, `decrypt_secret_policy()`, `deobfuscate_secret_policy_blob()`.
- `parse_policies_flags()` maps SCCM policy bitmasks to labels.
- `SCCMPoliciesAttack._run()` orchestrates registration, policy request, secret filtering, and processing.
- `register_client()`, `request_policies()`, `request_policy()`, and `secret_policy_process()` perform HTTP exchanges and extraction.

## Control Flow
`_run()` builds a management point URL and timestamped loot directory, defaults the client name and sleep interval, generates a private key and self-signed ConfigMgr certificate, writes them under `device/`, registers the client via `CCM_POST`, extracts the assigned GUID, sleeps for server-side policy availability, requests policy assignments, writes `policies.json` and `policies.raw`, filters policies marked `SECRET`, fetches each secret policy, decrypts CMS/EnvelopedData, handles collection settings compression when needed, writes `policy.txt`, deobfuscates secret blobs, writes each secret blob and embedded PowerShell script, and logs Network Access Account credentials if found.

## State and Persistence Behavior
Persistent output is a timestamped `*_sccm_policies_loot` tree containing generated device certificate/key/GUID/client name, raw and parsed policy lists, decrypted policies, deobfuscated secret blobs, and embedded scripts. The attack mutates SCCM server state by registering a client identity. Local config fields are defaulted in-place for client name and sleep duration.

## Dependencies and Integration Points
It depends on `cryptography`, `pyasn1_modules.rfc5652`, `pyasn1.codec.der.decoder`, `zlib`, `xml.etree.ElementTree`, `datetime`, `sleep`, `base64`, `binascii`, and `impacket.LOG`. It is mixed into `HTTPAttack` and assumes an HTTP client with ConfigMgr verbs and standard response access.

## Risks and Edge Cases
- The default sleep is 180 seconds, making tests and operations slow.
- Parsing assumes multipart boundaries, UTF-16 payloads, XML shapes, and SCCM policy schemas.
- Decryption supports only selected RSA/OAEP key wrapping and 3DES/AES-CBC content OIDs.
- `deobfuscate_secret_policy_blob()` can reference an unset `block_cipher_algorithm` for unknown prefixes.
- Loot may include sensitive private keys, Network Access Account credentials, and scripts.
- Some `except` blocks swallow parse/decode failures and continue with partial output.

## Test Signals
Unit tests should cover payload generation signatures, UTF-16/BOM handling, policy flag parsing, multipart decompression, CMS decryption for supported OIDs, deobfuscation for known blob prefixes, and XML extraction of NAA credentials and embedded scripts. Integration tests need a lab SCCM MP or captured responses.
