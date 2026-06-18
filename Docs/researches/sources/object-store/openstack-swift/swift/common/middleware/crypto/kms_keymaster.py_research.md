# sources/object-store/openstack-swift/swift/common/middleware/crypto/kms_keymaster.py

## Purpose
`kms_keymaster.py` adapts `BaseKeyMaster` to retrieve root encryption secrets from an external KMS through Castellan, commonly Barbican. It supports Keystone password credentials and multikey rotation.

## Important APIs, Types, and Functions
`KmsKeyMaster` defines config option names, section name, and `_get_root_secret()`. The factory returns `KmsKeyMaster(app, conf)`.

## Control Flow
`_get_root_secret()` builds a Castellan Keystone password context from auth, user, project, domain, trust, and reauthentication options. It creates an `oslo_config.cfg.ConfigOpts`, sets Castellan defaults including auth endpoint, Barbican endpoint, API class, and optional Barbican region, enables Castellan logging, then creates `key_manager.API`. For each `key_id*` option, it retrieves the key, rejects missing values, verifies AES algorithm, at least 256 bits, and RAW format, encodes returned secret material to bytes if needed, and returns root secrets keyed by Swift secret id.

## State and Persistence
KMS secrets are external persistent state. Retrieved root secrets are held in memory by `BaseKeyMaster`; derived keys and crypto metadata are handled by base keymaster and encryption middleware.

## Dependencies and Integration Points
It depends on Castellan, Keystone password credentials, Oslo config, Swift multikey parsing, and `BaseKeyMaster`. It is a drop-in replacement for local root-secret keymaster in the proxy pipeline.

## Risks and Edge Cases
Startup and reload depend on external KMS reachability and credentials. The broad `except Exception` around key validation converts any validation-time error into a symmetric-key type error, which can obscure the exact cause. RAW format and AES length checks are essential because base key derivation assumes raw high-entropy secret bytes. Region and endpoint misconfiguration will fail at retrieval time.

## Test Signals
Tests should cover construction of Keystone context, Castellan defaults, Barbican region handling, missing key returns, invalid algorithm/bit length/format, non-bytes encoded secret conversion, multikey parsing, active-root-secret validation from base, and external API exceptions.
