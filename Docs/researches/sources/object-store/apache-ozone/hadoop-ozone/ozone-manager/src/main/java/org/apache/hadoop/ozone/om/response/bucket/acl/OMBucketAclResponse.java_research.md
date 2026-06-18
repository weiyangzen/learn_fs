# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/bucket/acl/OMBucketAclResponse.java

Purpose: `OMBucketAclResponse` persists bucket ACL changes.

Important APIs and types: It stores updated `OmBucketInfo`, annotates `BUCKET_TABLE`, and checks `getOMResponse().getSuccess()` inside `addToDBBatch`.

Control flow: Base `checkAndUpdateDB` gates on OK status; this class adds a success flag check so no-op ACL responses do not write.

State and persistence behavior: Applied ACL changes update the bucket table. Failed or non-applied changes do not write.

Dependencies and integration points: It integrates bucket ACL request classes with metadata persistence.

Risks and test signals: Tests should cover add existing/remove missing no-op, applied ACL update, and failed response constructor behavior.
