<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/s3/S3SecretCacheProvider.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/s3/S3SecretCacheProvider.java

Purpose: Factory interface for constructing S3 secret cache implementations from Ozone configuration.

Important APIs/types/functions: Declares `S3SecretCache get(Configuration conf)`. Provides built-in `IN_MEMORY` provider that returns a new `S3InMemoryCache`.

Control flow and persistence: No persistent state in the interface. The in-memory provider creates runtime cache state only.

Dependencies and integration: Used by S3 secret manager setup to decouple cache choice from manager code. Depends on Hadoop `Configuration`, `S3SecretCache`, and `S3InMemoryCache`.

Risks and test signals: Cache provider instances can affect secret lookup freshness and memory usage. Tests should verify configured provider loading, default in-memory behavior, cache expiration/capacity integration, and that a new cache instance is created as expected.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/s3/S3SecretCacheProvider.java -->
