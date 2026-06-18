# sources/object-store/apache-ozone/hadoop-ozone/common/src/test/java/org/apache/hadoop/ozone/security/acl/TestOzoneObjInfo.java

Purpose: tests `OzoneObjInfo` builder accessors and protobuf path parsing for Ozone authorization objects.

Important APIs/types/functions: exercises `OzoneObjInfo.Builder`, `build`, getters for volume/bucket/key, and `OzoneObjInfo.fromProtobuf`.

Control flow and state: builder tests check null and populated volume, bucket, and key combinations. Protobuf tests create KEY objects with paths both with and without a leading delimiter and with long nested key paths, including a trailing slash. `fromProtobuf` must preserve the full key suffix after volume and bucket.

Dependencies and integration points: uses `OzoneManagerProtocolProtos.OzoneObj`, `OZONE_URI_DELIMITER`, `OzoneObj.ResourceType`, and `OzoneObj.StoreType`. These objects feed ACL authorization requests.

Risks and test signals: catches path splitting bugs where nested key slashes are truncated or leading delimiter variants are misread. The test also documents that key name may exist even if volume/bucket are null when built directly.
