# sources/distributed-fs/tahoe-lafs/src/allmydata/grid_manager.py

## Purpose
Implements Tahoe-LAFS Grid Manager internal state, storage-server authorization certificates, JSON persistence, and runtime certificate verification predicates. A Grid Manager signs short JSON certificates binding a storage server public key to an expiry time; clients can then decide whether a server announcement is authorized by any configured Grid Manager key.

## Important APIs, Types, And Functions
`SignedCertificate` is an attrs-frozen container for JSON-encoded certificate bytes plus raw Ed25519 signature bytes. `load()` reads a JSON container with base32 signature text, while `marshal()` emits JSON-compatible bytes/signature fields.

`_GridManagerStorageServer` stores a user-facing server name, Ed25519 verifying key, and in-memory list of issued `SignedCertificate` objects. `public_key_string()` serializes the key in Tahoe's Ed25519 format.

`_GridManagerCertificate` is a parsed certificate record loaded from `name.cert.N` files, with filename, numeric index, expiry, and storage-server public key.

`create_grid_manager()` generates a new Ed25519 signing keypair and returns `_GridManager`. `load_grid_manager(config_path)` loads `config.json` from a directory or stdin, validates config version `0`, parses the private key, loads configured storage servers, and optionally validates stored certificate files. `save_grid_manager()` writes the marshaled config to stdout or `config.json`, creating a 0700 directory for file-backed configs.

`_GridManager.sign(name, expiry)` signs a canonical JSON certificate containing `expires`, `public_key`, and `version`. It immediately verifies its own signature before appending the certificate to the server's in-memory certificate list.

`parse_grid_manager_certificate()` validates the outer JSON certificate container shape. `validate_grid_manager_certificate()` verifies a signature and returns decoded certificate data, deliberately not checking expiry. `create_grid_manager_verifier(keys, certs, public_key, now_fn=None, bad_cert=None)` pre-validates signatures against configured Grid Manager keys and returns a zero-argument predicate that checks certificate public-key match and expiry at call time.

## Control Flow
Creation starts with Ed25519 key generation and an empty storage-server dict. Loading reads `config.json`, rejects unknown versions or missing/invalid private keys, then constructs each `_GridManagerStorageServer` from persisted public keys. For file-backed configs, `_load_certificates_for()` scans sequential `name.cert.0`, `name.cert.1`, ... files until a missing index stops the loop, validating signatures when the Grid Manager public key is known.

Signing requires an existing storage server name. It computes `expiration = current_datetime_with_zone() + expiry`, serializes certificate metadata with deterministic separators and sorted keys, signs those bytes, self-verifies, records the certificate on the server object, and returns it.

Verifier creation has two phases. If no Grid Manager keys are configured, it returns a predicate that always succeeds. Otherwise it verifies each alleged certificate against each key, calls `bad_cert` for failures, keeps only successfully decoded cert bodies, and returns a predicate that compares encoded `public_key` bytes and `expires > now`.

## State And Persistence
Persistent state lives under a Grid Manager config directory: `config.json` contains config version, private signing key, and storage-server public keys; certificate files are separate sequential files per server. `_GridManager` keeps mutable state in a `UnicodeKeyDict` and per-server certificate lists. The verifier caches signature-valid certificate bodies, but expiry is evaluated fresh through `now_fn()` on each predicate call.

## Dependencies And Integration Points
Depends on `allmydata.crypto.ed25519`, Tahoe `base32` and `jsonbytes`, Twisted `FilePath`, `attrs`, and `datetime`. CLI code and admin/client config paths call these helpers; tests reference `allmydata.test.test_grid_manager`, `allmydata.test.cli.test_grid_manager`, `allmydata.test.cli.test_admin`, client announcement tests, and `integration/test_grid_manager.py`.

## Risks And Edge Cases
The annotation on `_load_certificates_for(gm_key=Optional[...])` uses a typing object as the default instead of `None`; runtime behavior still treats it as not-None unless callers pass explicitly, but actual calls pass the public key. Certificate scanning stops at the first missing numeric file, so gaps hide later certificates. `bad_cert` may be called repeatedly for multi-key setups even if another key validates the same certificate. `validate_grid_manager_certificate()` does not enforce version, expiry, or public key binding; callers must layer those checks. `save_grid_manager()` writes private key material and relies on directory permissions, not atomic replace.

## Test Signals
Primary coverage is `src/allmydata/test/test_grid_manager.py` for load/save/sign/parse/verifier behavior, `src/allmydata/test/cli/test_grid_manager.py` for CLI operations, `src/allmydata/test/cli/test_admin.py` for certificate installation, client announcement tests for config integration, and `integration/test_grid_manager.py` for end-to-end Grid Manager workflows.
