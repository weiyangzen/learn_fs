# sources/object-store/apache-ozone/hadoop-ozone/common/src/test/java/org/apache/hadoop/ozone/om/helpers/TestOmMultipartPartInfo.java

Purpose: tests `OmMultipartPartInfo` conversion to/from protobuf and creation from `OmKeyInfo`.

Important APIs/types/functions: exercises `OmMultipartPartInfo.from`, `getProto`, `getFromProto`, getters for part name/number/ETag/data size/modification/object/update IDs/key locations, and validation of required protobuf fields.

Control flow and state: a valid part info is built from key metadata containing `OzoneConsts.ETAG`, converted to protobuf, decoded, and field-compared. Separate tests clear required fields one by one and expect `IllegalArgumentException`. Object ID and update ID are optional and default to 0 when missing.

Dependencies and integration points: uses OM protobuf `MultipartPartInfo` and `KeyLocationList`, `OmKeyInfo`, `OmKeyLocationInfoGroup`, HDDS `BlockID`, RATIS replication config, and SCM `Pipeline`.

Risks and test signals: protects multipart list-parts responses and persisted part metadata from missing required data. The missing-ETag test is important because S3 multipart semantics require stable part ETags.
