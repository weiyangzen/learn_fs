# sources/object-store/apache-ozone/hadoop-ozone/client/src/main/java/org/apache/hadoop/ozone/client/rpc/OzoneKMSUtil.java

Purpose: This final utility class centralizes client-side KMS and encryption-at-rest helpers for Ozone RPC clients, including decrypting encrypted data encryption keys, locating KMS provider URIs, creating key providers, validating crypto protocol versions, and resolving crypto codecs.

Important APIs and types: Important methods are `decryptEncryptedDataEncryptionKey`, `getKeyProviderMapKey`, `bytes2String`, `getKeyProviderUri`, `getKeyProvider`, `getCryptoProtocolVersion`, `checkCryptoProtocolVersion`, and `getCryptoCodec`. It uses Hadoop `KeyProvider`, `KeyProviderCryptoExtension`, `FileEncryptionInfo`, `CryptoProtocolVersion`, `CipherSuite`, `CryptoCodec`, `Credentials`, `UserGroupInformation`, `KMSUtil`, and Ozone `ConfigurationSource`.

Control flow: Decryption wraps file encryption info into an `EncryptedKeyVersion` and calls the crypto extension. KMS URI lookup first checks UGI credentials keyed by the Ozone namespace URI, then client configuration when no server KMS URI is supplied, then the OM-provided server URI when non-empty; resolved URIs are cached back into credentials. Codec lookup rejects unknown cipher suites and reports a specific OM exception if no codec is configured.

State and persistence behavior: The class has no instance state. It mutates UGI `Credentials` by storing the key-provider URI secret for a namespace, enabling tasks to reuse the provider mapping. Other behavior is validation or provider/codec construction.

Dependencies and integration points: Used by RPC client encryption paths and encrypted bucket reads/writes. It bridges Ozone configuration to Hadoop KMS and crypto APIs and supports `OzoneCryptoInputStream`/encrypted output setup through decrypted keys and codecs.

Risks: The static `keyProviderUriKeyName` is mutable only inside the class but not final. URI precedence is important: cached credentials can override later config/server changes. Empty `kmsUriSrv` deliberately means no server URI, while null means fall back to client config. Error messages expose crypto suite/protocol details but not key material.

Test signals: Tests should cover null key provider failure, successful encrypted key decryption, namespace credential cache hit/miss, client-config versus server-URI precedence, credential write-back, null server provider rejection, unsupported crypto protocol rejection, unknown cipher suite rejection, missing codec OMException, and UTF-8 byte conversion.
