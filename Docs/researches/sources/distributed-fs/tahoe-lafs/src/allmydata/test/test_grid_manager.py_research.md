# sources/distributed-fs/tahoe-lafs/src/allmydata/test/test_grid_manager.py

Purpose: tests Grid Manager configuration, storage server registration, certificate serialization/parsing, Ed25519 signing, certificate verification, and invalid certificate rejection. It protects the trust path that lets clients accept storage servers based on grid-manager-issued certificates.

Important APIs and types include `GridManagerUtilities`, `GridManagerVerifier`, and `GridManagerInvalidVerifier`. The implementation under test includes `config_from_string`, client `_valid_config`, `load_grid_manager`, `save_grid_manager`, `create_grid_manager`, `parse_grid_manager_certificate`, `create_grid_manager_verifier`, `SignedCertificate`, and Ed25519 key helpers.

Control flow first tests client config certificate loading by writing JSON certificate files and pointing `[grid_manager_certificates]` entries at them. Grid manager tests create a manager, add/remove storage server verifying keys, sign certificates with different expirations, verify signatures with the manager public key, marshal to JSON, save/load from a `config.json` directory, and parse certificate JSON. Invalid config tests omit version or private key, use malformed private keys, omit storage-server public keys, and include certificates with unsupported versions. Verification tests build a verifier from manager public keys, certificates, and a storage server public key and assert acceptance or rejection.

State and persistence behavior includes temporary certificate files, temporary grid-manager directories with `config.json` and `*.cert.*` files, JSON bytes serialization, and in-memory Ed25519 keypairs. There is no running storage server; the server identity is represented by public key strings.

Dependencies include Twisted `FilePath`, Hypothesis for invalid base32-like signatures, Tahoe node config parsing, client config validation schema, `jsonbytes`, grid manager implementation, Ed25519 crypto utilities, and `SyncTestCase`.

Risks covered include accepting malformed certificates, unknown keys in cert files, missing cert files, wrong certificate/config version numbers, missing or invalid private keys, signing unknown server names, serialization drift, bad signature acceptance, and mismatch between storage server identity and certificate contents. Residual risk is that expiry-time enforcement and multi-manager policy combinations are only lightly represented by signing and verification happy paths.

Test signals include exception messages for malformed inputs, equality of marshaled save/load data, direct Ed25519 signature verification returning `None`, parsed certificate key sets, `create_grid_manager_verifier` returning `True` for valid certs and `False` for Hypothesis-generated invalid signatures, and utility config methods returning expected manager/certificate lists.
