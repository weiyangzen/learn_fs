# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/bucket/acl/package-info.java

Purpose: This package documentation identifies the package as containing bucket ACL response classes.

Important APIs and types: The package currently centers on `OMBucketAclResponse`, which persists ACL mutations to `OmBucketInfo`.

Control flow: Bucket ACL requests produce responses that rely on `OMClientResponse` success gating and then write updated bucket metadata.

State and persistence behavior: State changes target `BUCKET_TABLE` rows containing bucket ACL lists.

Dependencies and integration points: The package connects bucket ACL request handlers, response DB batching, cleanup annotations, and OM metadata manager bucket-key derivation.

Risks and test signals: Package-level tests should cover add/remove/set ACL success and no-op paths, ensuring unchanged ACL operations do not write table rows unnecessarily.
