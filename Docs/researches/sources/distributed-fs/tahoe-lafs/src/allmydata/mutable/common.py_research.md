## sources/distributed-fs/tahoe-lafs/src/allmydata/mutable/common.py

### Purpose
This module contains shared mutable-file constants, exception types, and cryptographic key derivation helpers. It is imported by servermap, publish, retrieve, checker, repairer, and filenode code.

### Important APIs, Types, and Functions
Mode constants are `MODE_CHECK`, `MODE_ANYTHING`, `MODE_WRITE`, `MODE_READ`, and `MODE_REPAIR`, defining how thoroughly servermaps query peers and whether private-key/write information is needed. Exception types include `NotWriteableError`, `BadShareError`, `NeedMoreDataError`, `UncoordinatedWriteError`, `UnrecoverableFileError`, `NotEnoughServersError`, `CorruptShareError`, and `UnknownVersionError`. Crypto helpers are `encrypt_privkey(writekey, privkey)`, `decrypt_privkey(writekey, enc_privkey)`, and `derive_mutable_keys(keypair)`.

### Control Flow
`derive_mutable_keys` DER-serializes RSA public/private keys, hashes the private key to produce the SSK writekey, AES-encrypts the private key under that writekey, hashes the public key into the fingerprint, and returns `(writekey, encprivkey, fingerprint)`. `encrypt_privkey` and `decrypt_privkey` wrap Tahoe AES helper creation and data transform calls.

### State and Persistence Behavior
The module owns no mutable state. Its outputs become persistent mutable-file identity/authority data: write keys, encrypted private keys stored in shares, and public-key fingerprints embedded in capabilities and share validation.

### Dependencies and Integration Points
It depends on Tahoe AES/RSA crypto helpers and `hashutil`. `MutableFileNode.create_with_keys` calls `derive_mutable_keys` in a CPU thread. `servermap.py` and `retrieve.py` call `decrypt_privkey` to recover signing keys when write authority is available. `checker.py` uses common modes and corrupt-share errors.

### Risks and Edge Cases
These helpers sit on a security boundary. Changes to DER serialization, hash functions, AES mode, or prefix handling would break capability identity or make old mutable shares unreadable. `UncoordinatedWriteError.__repr__` carries user-facing guidance but no structured metadata. `NeedMoreDataError` includes offsets/lengths used by layout/retrieve logic and must remain consistent with share parsing.

### Test Signals
Mutable creation tests compare derived key/fingerprint behavior through caps, web tests derive expected mutable keys from generated RSA keys, and retrieve/servermap tests exercise private-key decryption paths. Integration web tests call `derive_mutable_keys` to construct expected mutable URIs.
