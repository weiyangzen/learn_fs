# File Research: sources/os/plan9/plan9/sys/src/cmd/auth/factotum/rsa.c

Implements factotum’s `rsa` protocol for old SSH challenge response plus signing and verification roles. Supported roles are `client`, `sign`, and `verify`.

For `client`, reads iterate over candidate public moduli, then a written challenge is private-key decrypted after confirmation checks. For `sign`, a caller writes a hash and reads a PKCS#1-padded RSA signature. For `verify`, caller writes hash then signature and reads `ok` or failure text.

`readrsapriv` parses public and private mpints from key attrs; `rsaaddkey` stores an `RSApriv` in `Key.priv`. The signing path builds ASN.1 `DigestInfo` for SHA1 or MD5 and applies PKCS#1 v1.5-style padding.
