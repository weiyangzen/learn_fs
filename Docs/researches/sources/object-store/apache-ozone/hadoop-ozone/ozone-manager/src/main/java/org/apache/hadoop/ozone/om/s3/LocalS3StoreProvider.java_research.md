<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/s3/LocalS3StoreProvider.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/s3/LocalS3StoreProvider.java

Purpose: Provides the local OM metadata manager as the S3 secret store implementation.

Important APIs/types/functions: Implements `S3SecretStoreProvider`. Constructor stores an `OmMetadataManagerImpl`; `get(Configuration)` returns that metadata manager as `S3SecretStore`.

Control flow and persistence: No independent persistence. The returned `OmMetadataManagerImpl` owns local `S3_SECRET_TABLE` storage and related batching.

Dependencies and integration: Used as `S3SecretStoreConfigurationKeys.DEFAULT_SECRET_STORAGE_TYPE`. Integrates S3 secret manager configuration with local OM RocksDB-backed storage.

Risks and test signals: This provider ignores the passed configuration, which is appropriate for local storage but should be explicit in tests. Tests should verify default provider instantiation, returned object identity, and compatibility with `S3SecretStore` methods.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/s3/LocalS3StoreProvider.java -->
