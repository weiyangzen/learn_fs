# sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/OmKeyLocationInfo.java

Purpose: OM wrapper around HDDS `BlockLocationInfo` representing one block/subkey location for a key.

Important APIs/types/functions: Builder fluently sets block ID, pipeline, length, offset, block token, multipart part number, and create version. `getProtobuf` emits `KeyLocation`, optionally omitting pipeline/token fields. `getFromProtobuf` reconstructs block ID, length, offset, pipeline, token, create version, and part number.

Control flow and state: Serialization always writes block ID, length, offset, create version, and part number. When `ignorePipeline` is false, it includes token and pipeline if present. Pipeline can be null for older key versions.

State and persistence behavior: Embedded in `OmKeyInfo` and multipart part protobufs. DB codecs typically omit pipeline data to avoid persisting volatile pipeline state; network responses include it.

Dependencies and integration points: Used by key block allocation/commit/read responses, `OmKeyLocationInfoGroup`, and multipart part metadata. Depends on HDDS block/pipeline/token types and `OMPBHelper`.

Risks: Null block ID would fail serialization. Persisted data without pipeline must be refreshed or tolerated by clients depending on operation.

Test signals: Proto round trips with token/pipeline present and omitted, create-version/part-number preservation, and DB vs network serialization differences.
