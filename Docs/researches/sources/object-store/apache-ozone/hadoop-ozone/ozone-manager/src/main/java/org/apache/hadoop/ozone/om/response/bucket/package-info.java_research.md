# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/response/bucket/package-info.java

Purpose: This package documentation marks the package as containing bucket response classes.

Important APIs and types: The package includes create, delete, owner, property, and ACL-related response implementations that persist `OmBucketInfo` and sometimes `OmVolumeArgs`.

Control flow: Request handlers validate and update cache, then response classes apply the same mutation to RocksDB batch operations during transaction replay/application.

State and persistence behavior: State changes primarily target `BUCKET_TABLE`, with create/delete also updating `VOLUME_TABLE` for namespace usage.

Dependencies and integration points: The package integrates bucket request handlers, `OMClientResponse`, cleanup annotations, and OM metadata table key helpers.

Risks and test signals: Tests should verify each response declares all touched tables, persists expected bucket/volume records, and handles OK-but-no-op responses where supported.
