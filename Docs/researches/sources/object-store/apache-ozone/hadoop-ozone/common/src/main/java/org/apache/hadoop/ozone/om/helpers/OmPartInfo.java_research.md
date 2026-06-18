<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/OmPartInfo.java -->
# sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/OmPartInfo.java

## Purpose

`OmPartInfo` is the immutable Java representation of one multipart upload part. It records the part number, backing part key/name, modification time, logical size, and optional eTag.

## Important APIs, Types, And Functions

The constructor initializes all fields, getters expose each value, and `getProto()` converts to `OzoneManagerProtocolProtos.PartInfo`. The eTag field is optional and is only set in protobuf when non-null.

## Control Flow, State, And Persistence

This is a value object with final fields. OM multipart list code constructs it from persisted multipart metadata or protobuf responses, and protocol code serializes it with `getProto()`. The object itself has no mutation or storage side effects.

## Dependencies And Integration Points

It depends only on the multipart `PartInfo` protobuf. It is consumed by `OmMultipartUploadListParts`, complete-multipart responses, and S3 gateway translation logic that must preserve AWS-compatible part number, size, modified time, and eTag data.

## Risks And Test Signals

There is no validation of part number range, name, or size, so invalid data must be rejected upstream. Test signals are protobuf round trips with and without eTag, ordered part listings, large part sizes, and boundary part numbers.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/OmPartInfo.java -->
