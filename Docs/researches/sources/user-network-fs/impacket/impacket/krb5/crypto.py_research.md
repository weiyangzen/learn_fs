# sources/user-network-fs/impacket/impacket/krb5/crypto.py

Purpose: implements Kerberos cryptographic profiles for DES-CBC-MD5, DES3, AES128/256 CTS-HMAC-SHA1-96, and RC4-HMAC, plus checksums, string-to-key, PRF, CF2, and key derivation helpers.

Important APIs/types: public classes/constants include `Enctype`, `Cksumtype`, `InvalidChecksum`, and `Key`. Public helpers include `random_to_key()`, `string_to_key()`, `encrypt()`, `decrypt()`, `prf()`, `make_checksum()`, `verify_checksum()`, `get_matching_aes_key()`, `get_kerberos_key_for_enctype()`, `cf2()`, and `generate_kerberos_keys()`. Internal profiles `_SimplifiedEnctype`, `_DESCBC`, `_DES3CBC`, `_AESEnctype`, `_AES128CTS`, `_AES256CTS`, `_RC4`, and checksum profiles back `_enctype_table` and `_checksum_table`.

Control flow and state: profile methods derive usage-specific keys, add confounders, encrypt, append/truncate HMACs, verify in constant time, and strip confounders. AES implements ciphertext stealing; RC4 implements RFC 4757 usage mapping and errata fallback for key usage 9. There is no persistent state; randomness comes from `os.urandom`.

Dependencies and integration: depends on PyCryptodome ciphers/hashes/KDF, `six`, `struct`, `binascii`, and Kerberos constants. `kerberosv5.py`, `ccache.py`, `gssapi.py`, `kpasswd.py`, and `pac.py` rely on these profiles for protocol key usages and checksum generation.

Risks and test signals: the top-level `encrypt()` wrapper does `bytes(confounder)`, which raises for `None`; many callers use profile methods directly where `None` is supported. DES support is legacy and includes hand-rolled parity/string-to-key code. `generate_kerberos_keys()` infers AD salts and raw UTF-16 password handling. Tests should use known RFC vectors for AES/RC4/DES3, bad-MAC `InvalidChecksum`, wrong key length, AES key selection, CF2, PAC checksum types, and the `encrypt(..., confounder=None)` wrapper edge.
