# sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/security/OzoneTokenIdentifier.java

Purpose: Token identifier for Ozone Manager delegation tokens and S3 authentication tokens. It extends Hadoop's delegation token identifier with OM-specific secret-key/certificate identity, S3 auth fields, and OM service ID.

Important APIs and types: Constants and fields include `KIND_NAME`, deprecated `omCertSerialId`, `secretKeyId`, token `Type`, S3 access/signature/string-to-sign, and `omServiceId`. Key methods are constructors, `getKind`, `fromUniqueSerializedKey`, `toProtoBuf`, `write`, `readFields`, `readProtoBuf`, factories, equality/hash, accessors, and nested `TokenInfo`.

Control flow: Current serialization writes the `OMTokenProto` bytes directly and reads them back from a `DataInputStream`. `readProtoBuf` constructs identifiers from proto fields. `fromUniqueSerializedKey` supports explicit legacy deserialization: it reads superclass fields and a VInt token type, then either S3 fields or delegation token key identity plus service ID. For delegation tokens it treats a UUID-looking value as `secretKeyId`, otherwise as deprecated certificate serial ID.

State and persistence behavior: This class is serialized into token identifiers stored in Hadoop credentials and OM token databases. `TokenInfo` stores renew date, password copy, and optional tracking ID. Setters enforce that `omCertSerialId` and `secretKeyId` are not both valid.

Dependencies and integration points: Used by OM token managers, Hadoop security token framework, `OzoneDelegationTokenSelector`, OM protobuf token messages, S3 authentication flows, and secret-key/certificate migration compatibility.

Risks: `readFields` casts `DataInput` to `DataInputStream`, so non-stream inputs would fail. `toString` includes signature, string-to-sign, and access key ID, which is sensitive if logged. `equals` does not compare S3-specific fields or token type, so equality is delegation-token oriented. Serialization compatibility is high-risk because stored tokens must survive upgrades.

Test signals: Round-trip protobuf serialization for delegation and S3 tokens, legacy unique-key parsing for UUID and non-UUID key IDs, mutual exclusion of certificate and secret key IDs, `TokenInfo` password defensive copy, equality semantics, and secure logging review for `toString`.
