<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/s3/S3SecretStoreConfigurationKeys.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/s3/S3SecretStoreConfigurationKeys.java

Purpose: Defines configuration keys and defaults for S3 secret store provider and cache behavior.

Important APIs/types/functions: Final utility class with private constructor. Constants include `S3_SECRET_STORAGE_TYPE`, `DEFAULT_SECRET_STORAGE_TYPE` (`LocalS3StoreProvider.class`), `CACHE_PREFIX`, `CACHE_LIFETIME`, `DEFAULT_CACHE_LIFETIME` (600), `CACHE_MAX_SIZE`, and `DEFAULT_CACHE_MAX_SIZE` (`Long.MAX_VALUE`).

Control flow and persistence: No runtime control flow or persistence. Values are consumed by configuration loading elsewhere.

Dependencies and integration: Integrated by S3 secret manager/provider initialization and cache setup. Uses the `ozone.secret.s3.store.` prefix.

Risks and test signals: Key spelling and default values form operator-facing compatibility. Tests should verify default local provider selection, cache lifetime unit interpretation, max-size default behavior, and configuration override parsing.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/s3/S3SecretStoreConfigurationKeys.java -->
