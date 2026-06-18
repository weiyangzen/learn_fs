# sources/user-network-fs/impacket/impacket/examples/ntlmrelayx/utils/shadow_credentials.py

Purpose: builds certificates and `msDS-KeyCredentialLink` binary values used by Shadow Credentials attacks, and exports generated credentials in PFX or PEM format.

Important APIs and control flow: `getTicksNow()` returns Windows/.NET ticks since 1601 UTC. `getDeviceId()` returns UUID bytes. `createSelfSignedX509Certificate()` creates a 2048-bit RSA key and ten-year self-signed CA certificate. `KeyCredential.raw_public_key()` serializes RSA public key material in the expected `RSA1` layout. `dumpBinary()` packs version, key identifier, key hash over binary properties, and binary properties. `toDNWithBinary2String()` formats the blob as an AD DN-Binary string. `exportPFX()` and `exportPEM()` create directories and write credential files.

State and persistence: `KeyCredential` keeps serialized fields in memory. `exportPFX()` writes `.pfx`; `exportPEM()` writes `_cert.pem` and `_priv.pem`. Directory creation is persistent.

Dependencies and integration: uses `cryptography`, PyCryptodome number conversion, hashing/base64/UUID/date utilities, and AD attack code that writes the generated DN-Binary string to LDAP attributes.

Risks and test signals: PFX export requires a password because it calls `password.encode()`. PEM private keys are unencrypted. Field packing must match Windows expectations exactly. Tests should validate field structure lengths, ticks range, DN-Binary formatting, exported file names/content, directory creation, and compatibility with LDAP shadow credential consumers.
