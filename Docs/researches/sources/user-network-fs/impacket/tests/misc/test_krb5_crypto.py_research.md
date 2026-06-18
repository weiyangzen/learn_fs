# sources/user-network-fs/impacket/tests/misc/test_krb5_crypto.py

Purpose: Validates Kerberos crypto implementations against deterministic vectors across AES, DES3, RC4, and DES string-to-key.

Important APIs, types, and functions: Uses `Key`, `Enctype`, `encrypt`, `decrypt`, `Cksumtype`, `verify_checksum`, `_zeropad`, `string_to_key`, `prf`, and `cf2`.

Control flow: Each test builds keys from hex or string-to-key inputs, runs encryption/decryption, checksum verification, PRF, or CF2 combination, and compares exact bytes.

State and persistence behavior: Pure in-memory crypto tests. No tickets or keytabs are read.

Dependencies and integration points: Core coverage for Kerberos AS/TGS, PAC signing, and GSSAPI code paths that rely on these primitives.

Risks: Crypto vector changes may indicate serious interoperability regressions. DES/RC4 legacy paths remain covered despite weaker algorithms because Kerberos deployments can still encounter them.

Test signals: Strong signal for AES128/AES256 encryption/checksum/string-to-key/PRF/CF2, DES3 encryption/checksum/string-to-key/CF2, RC4 encryption/checksum/string-to-key/CF2, and DES MD5 string-to-key.
