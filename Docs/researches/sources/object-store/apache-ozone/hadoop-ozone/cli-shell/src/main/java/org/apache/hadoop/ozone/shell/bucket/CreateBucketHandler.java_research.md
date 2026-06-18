## sources/object-store/apache-ozone/hadoop-ozone/cli-shell/src/main/java/org/apache/hadoop/ozone/shell/bucket/CreateBucketHandler.java

Purpose: bucket `create` command supporting owner, encryption, GDPR metadata, layout, default replication, and quota options.

Important APIs and control flow: builds `BucketArgs` with default storage type/versioning and owner defaulting to current user. Optional flags set bucket layout (`fso`, `obs`, or enum), GDPR metadata, BEK, default replication config from explicit replication params, and parsed space/namespace quota. It resolves the volume and calls `createBucket`, printing the created bucket in verbose mode.

State and dependencies: persists new bucket metadata through OM RPCs. Depends on `BucketArgs`, `OzoneQuota`, replication config wrappers, `UserGroupInformation`, and `BucketLayout`.

Risks and test signals: empty encryption key is rejected locally; layout aliases must stay aligned with server-supported layouts. Quota and replication parsing errors occur before RPC. No direct tests in this subset.
