# sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/BucketEncryptionKeyInfo.java

Purpose: Immutable bucket encryption key descriptor containing crypto protocol version, cipher suite, and KMS key name.

Important APIs/types/functions: Constructor and nested `Builder` set `CryptoProtocolVersion`, `CipherSuite`, and key name. Accessors expose those values. `equals` and `hashCode` compare all fields.

Control flow and state: No runtime branching beyond equality. The builder does not validate nulls.

State and persistence behavior: Embedded in bucket arguments/info and converted to protobuf through `OMPBHelper`, making it part of persisted and RPC bucket metadata when encryption is enabled.

Dependencies and integration points: Used by `OmBucketArgs`, `OmBucketInfo`, and encryption-zone/bucket creation flows. Depends on Hadoop crypto types.

Risks: The class permits null fields; callers must validate before persisting or enforcing encryption. Deprecated setter paths in bucket builders skip entries whose key name is null.

Test signals: Builder equality/hash tests, protobuf conversion through bucket metadata, and null-key filtering in bucket builders.
