<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/cryfs-config/src/config/encryption/inner.rs -->
# sources/security-integrity/cryfs/crates/cryfs-config/src/config/encryption/inner.rs

Purpose: inner layer of config encryption: encrypts the serialized `CryConfig` with the filesystem cipher and records the cipher name.

Important APIs/types/functions: `InnerConfigLayout` stores header, cipher name, and encrypted config bytes. `InnerConfig::encrypt`, `decrypt`, `deserialize`, and `serialize` implement the layer. Header is `cryfs.config.inner;0`, and plaintext is padded to `CONFIG_SIZE` 900 bytes before encryption.

Control flow: encryption selects cipher from `config.cipher`, serializes JSON into a `Data` buffer with room for cipher overhead, pads to fixed size, encrypts, and stores bytes. Decryption looks up the stored cipher, decrypts, removes padding, deserializes `CryConfig`, and ensures the internal config cipher matches the layer cipher.

State and persistence: serialized inside the outer config layer; hides exact JSON length up to 900 bytes.

Dependencies/integration: uses `binrw`, dynamic cipher lookup, `Data`, and padding helpers.

Risks/test signals: config larger than 900 bytes errors and requires increasing `CONFIG_SIZE`. Header error text says "outer config" although this is inner config.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/cryfs-config/src/config/encryption/inner.rs -->
