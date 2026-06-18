# File Research: sources/os/plan9/9front/sys/src/cmd/auth/factotum/rsa.c

Factotum RSA protocol module for legacy SSH challenge response, signing, and verification.

Key responsibilities:
- Parses RSA public/private key attributes into `RSApriv`.
- Client role exposes public keys, accepts a hex challenge, and returns RSA private-key decrypted response.
- Sign role accepts a hash and returns PKCS#1 padded RSA signature bytes.
- Verify role accepts a hash and signature and returns `ok` or failure text.
- Supports hash algorithms `sha1`, `md5`, and `sha256`.
- Builds simple ASN.1 DigestInfo structures for PKCS#1 signing/verification.
- Requires confirmation for key use when key attributes request it.

Dependencies:
- Uses factotum keyring, libsec RSA/mpint helpers, ASN.1 encode conventions, and hash constants.

Notable risks:
- Only private keys are usable for client/signing operations.
- ASN.1 length handling is intentionally simple for short DigestInfo values.
