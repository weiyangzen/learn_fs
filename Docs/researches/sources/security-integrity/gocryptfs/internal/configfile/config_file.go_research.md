# sources/security-integrity/gocryptfs/internal/configfile/config_file.go

Purpose: This file reads, writes, creates, validates, encrypts, and decrypts `gocryptfs.conf` files, including feature flags and master-key wrapping.

Important APIs and types: `ConfFile`, `FIDO2Params`, and `CreateArgs` model persisted config and creation inputs. `Create`, `Load`, `LoadAndDecrypt`, `DecryptMasterKey`, `EncryptKey`, `WriteFile`, `getKeyEncrypter`, and `ContentEncryption` are core APIs.

Control flow and state: `Create` assembles feature flags, generates or accepts a master key, encrypts it with an scrypt-derived key and content encryption, wipes temporary keys, validates, and atomically writes JSON. `Load` unmarshals and validates. `WriteFile` writes `filename.tmp`, syncs, and renames over the target.

Dependencies and integration points: Integrates content encryption, crypto core, scrypt KDF, FIDO2 metadata, init/passwd/mount/xray flows, and exit-code typed errors.

Risks and test signals: This is security-critical. Risks include secret leakage, wrong feature flags, non-atomic writes, weak KDF parameters, and backward compatibility. Signals include config fixture tests, wrong-password errors, timing/KDF tests, and feature validation tests.
