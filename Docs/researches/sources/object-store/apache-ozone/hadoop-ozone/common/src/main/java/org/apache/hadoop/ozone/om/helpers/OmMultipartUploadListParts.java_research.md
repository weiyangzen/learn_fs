<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/OmMultipartUploadListParts.java -->
# sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/OmMultipartUploadListParts.java

## Purpose

`OmMultipartUploadListParts` is the OM-side response model for listing the parts of one multipart upload. It carries the upload replication configuration, pagination marker state, truncation state, and an ordered mutable list of `OmPartInfo` entries.

## Important APIs, Types, And Functions

The public API is the constructor, `addPart`, `addPartList`, `addProtoPartList`, and getters for `nextPartNumberMarker`, `truncated`, `partInfoList`, and `replicationConfig`. `addProtoPartList` is the conversion boundary from protobuf `PartInfo` to helper objects.

## Control Flow, State, And Persistence

The class is an in-memory DTO. OM handlers create it with the replication config and pagination state, append Java or protobuf part records, and return it through protocol translators. It does not persist itself; persistence belongs to multipart upload metadata tables and the `PartInfo` protobuf fields.

## Dependencies And Integration Points

It depends on `ReplicationConfig`, `OmPartInfo`, and `OzoneManagerProtocolProtos.PartInfo`. It integrates with `OzoneManagerProtocol.listParts`, S3 multipart list-parts responses, and translator code that maps OM helper results back into protobuf or REST responses.

## Risks And Test Signals

The internal list is returned directly, so callers can mutate it. Pagination correctness depends on the caller setting the marker and truncation flag consistently with the part list. Test with empty uploads, exact page-size boundaries, truncated listings, eTag propagation, and both RATIS and EC replication configs.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/OmMultipartUploadListParts.java -->
