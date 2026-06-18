# sources/distributed-fs/tahoe-lafs/src/allmydata/test/certs.py

## Purpose
Supplies simple certificate-generation utilities for tests that need TLS material. It creates RSA private keys, self-signed localhost certificates, and writes keys/certificates to Twisted `FilePath` objects in PEM form.

## Important APIs, Types, And Functions
`generate_private_key()` creates a 2048-bit RSA key. `generate_certificate(private_key, expires_days=10, valid_in_days=0, org_name="Yoyodyne")` builds and signs a self-signed certificate with an organization name and localhost SAN. `cert_to_file()` writes a certificate PEM. `private_key_to_file()` writes an unencrypted traditional OpenSSL private-key PEM.

## Control Flow
Tests call key generation, pass the key into certificate generation, then persist either object to temporary files. Certificate validity starts at the earlier of the requested start and expiration time and ends at the requested expiration time, allowing tests to create expired or not-yet-valid edge cases.

## State And Persistence
No module state is retained. Persistence is explicit through `FilePath.setContent()` writes of PEM bytes.

## Dependencies And Integration Points
Depends on `cryptography.x509`, RSA primitives, SHA-256 signing, serialization helpers, `NameOID`, and Twisted `FilePath`. Integrates with HTTPS/TLS tests elsewhere in the suite.

## Risks And Test Signals
The private key is intentionally unencrypted and only suitable for tests. Use of `datetime.utcnow()` can produce boundary-sensitive validity tests. Test signals include successful TLS setup with localhost SAN, expired/future certificate scenarios, PEM readability by Twisted/OpenSSL consumers, and deterministic failure when malformed paths are supplied.
