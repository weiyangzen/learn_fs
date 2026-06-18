# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/ha/io/ScmManagedSecretKeyCodec.java

Purpose: SCM HA codec for `ManagedSecretKey` values used by secret-key replication and checkpoint reinitialization.

Important APIs and types: Serializes with `ManagedSecretKey.toProtobuf()` and deserializes by parsing `SCMSecretKeyProtocolProtos.ManagedSecretKey` followed by `ManagedSecretKey.fromProtobuf`.

Control flow: Serialization wraps the non-shaded protobuf bytes in a shaded Ratis `ByteString`. Deserialization catches non-shaded protobuf parse exceptions and rethrows shaded `InvalidProtocolBufferException`.

State and persistence behavior: Stateless; encoded secret keys are transported in Ratis payloads rather than stored by this codec directly.

Dependencies and integration points: Registered in `ScmCodecFactory`; used by `SecretKeyStateInvoker` and list codec for key lists.

Risks and test signals: Secret key wire compatibility depends on protobuf schema stability. Tests should cover round trips, malformed bytes, list round trips, and preservation of key id/material/metadata fields.
