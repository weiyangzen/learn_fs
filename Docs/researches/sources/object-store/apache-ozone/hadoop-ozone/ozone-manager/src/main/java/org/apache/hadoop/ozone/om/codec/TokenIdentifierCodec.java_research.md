# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/codec/TokenIdentifierCodec.java

Purpose: `TokenIdentifierCodec` serializes and deserializes `OzoneTokenIdentifier` keys for OM's delegation token table.

Important APIs and types: It is a singleton `Codec<OzoneTokenIdentifier>` exposed by `get()`. It implements `getTypeClass`, `toPersistedFormat`, `fromPersistedFormatImpl`, and `copyObject`.

Control flow: Serialization requires a non-null token and writes its protobuf bytes. Deserialization first tries `OzoneTokenIdentifier.readProtoBuf`; if that fails, it tries the legacy `fromUniqueSerializedKey` format and suppresses the first exception on the second if both fail.

State and persistence behavior: The codec is stateless. It defines persistent encoding for delegation token table keys and preserves backward compatibility with older unique-key serialization.

Dependencies and integration points: `OMDBDefinition.DELEGATION_TOKEN_TABLE_DEF` uses this codec. Token managers depend on it to read existing tokens after upgrade.

Risks and test signals: `copyObject` returns the same mutable object if `OzoneTokenIdentifier` is mutable. Tests should cover protobuf round trips, legacy bytes fallback, double-failure suppressed exceptions, null serialization rejection, and compatibility with existing token DB entries.
