# sources/user-network-fs/impacket/impacket/examples/ntlmrelayx/attacks/httpattacks/adcsattack.py

## Purpose
`adcsattack.py` implements the HTTP Web Enrollment variant of an AD CS relay attack. It can enumerate certificate templates from `/certsrv/certrqxt.asp` or submit a CSR to `/certsrv/certfnsh.asp`, retrieve the issued certificate, and write a PKCS#12 file for later authentication.

## Important APIs, Types, and Functions
- `ELEVATED` is a module-level list used to skip repeated certificate requests for the same username.
- `ADCSAttack._run()` performs template enumeration or certificate request/retrieval.
- Static helpers `generate_csr()`, `generate_pfx()`, and `generate_certattributes()` build the CSR, PKCS#12 payload, and AD CS request attributes.
- `enum_templates()` parses `<Option Value="...">` rows from the web enrollment template page.
- `_extract_certificate_identity()` pulls CN, UPN OtherName, or DNS SAN from a certificate.
- `_sanitize_filename()` normalizes output filenames.

## Control Flow
`_run()` generates a 4096-bit RSA key, skips if the username is already in `ELEVATED`, optionally enumerates templates, selects a template (`Machine` for machine accounts and `User` otherwise by default), builds a CSR and form body, POSTs to `certfnsh.asp`, extracts `ReqID`, GETs `certnew.cer`, converts the certificate to a cryptography object, serializes a PFX, and writes it into `config.lootdir`. On file write failure it logs base64 PFX data instead.

## State and Persistence Behavior
State is held in the global `ELEVATED` list and in generated private key/certificate objects. Persistent output is a `.pfx` file under `config.lootdir`, or base64 material in logs if writing fails. The attack mutates the AD CS CA by creating a certificate request and issuing a certificate.

## Dependencies and Integration Points
It depends on `OpenSSL.crypto`, `cryptography.x509`, `cryptography.hazmat.primitives.serialization.pkcs12`, `urllib.parse`, `re`, `base64`, `os`, and `impacket.LOG`. It is mixed into `HTTPAttack` and assumes an HTTP client compatible with `request()`/`getresponse()`.

## Risks and Edge Cases
- Global `ELEVATED` is process-wide and keyed only by username, not target CA or template.
- HTML parsing is regex-based and fragile to localized or changed Web Enrollment pages.
- PFX is serialized without encryption.
- Alternate names can create certificates for identities other than the relayed username.
- If `config.lootdir` creation fails, certificate material is logged.

## Test Signals
Tests should fake HTTP responses for template enumeration, successful ReqID extraction, failed status, missing ReqID, certificate identity extraction, filename sanitization, and PFX writing fallback. Integration tests need an AD CS Web Enrollment lab with user and machine templates.
