# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/security/token/OzoneBlockTokenIdentifier.java

## Purpose
Hadoop token identifier for short-lived HDDS block access tokens. It binds an owner, service/block ID, access modes, expiry, secret key ID, and maximum allowed length into a protobuf-serialized token payload.

## Important APIs and types
`KIND_NAME` is `HDDS_BLOCK_TOKEN`. Constructors accept owner, `BlockID` or block service string, access-mode set, expiry millis, and max length. `getTokenService(BlockID)` derives token service from the container block ID. Accessors expose service, expiry millis, access modes, max length, and kind. Serialization APIs are `readFields`, `readFromByteArray`, `readFieldsProtobuf`, `write`, and `getBytes`.

## Control flow and state
The default constructor supports Hadoop deserialization. `readFields` requires a mark-supported `DataInputStream`, parses `BlockTokenSecretProto`, and populates inherited owner/expiry/secret-key fields plus block ID, modes, and max length. `getBytes` writes the same fields back to protobuf. Null modes become an empty `EnumSet`.

## Dependencies and integration points
It extends `ShortLivedTokenIdentifier`, uses `HddsProtos.BlockTokenSecretProto`, `AccessModeProto`, `BlockID`, Hadoop `Text`, and `ProtobufUtils` for UUID conversion. `OzoneBlockTokenSelector`, `BlockLocationInfo`, and container protocol calls carry or select tokens of this kind.

## Risks and test signals
Tests should cover protobuf round trips, empty access-mode handling, owner fallback through inherited `getUser`, secret-key ID preservation, equality/hash code, and invalid input streams. `EnumSet.copyOf(token.getModesList())` fails for an empty list, so deserialization tests should verify expected behavior for tokens without modes.
