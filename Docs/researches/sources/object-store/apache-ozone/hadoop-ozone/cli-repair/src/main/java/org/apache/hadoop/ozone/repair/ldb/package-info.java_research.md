## sources/object-store/apache-ozone/hadoop-ozone/cli-repair/src/main/java/org/apache/hadoop/ozone/repair/ldb/package-info.java

Purpose: package Javadoc marker for `org.apache.hadoop.ozone.repair.ldb`. The comment says "OM related repair tools", but the package actually holds generic LDB/RocksDB repair commands.

APIs and integration: no code API. It participates only in generated package documentation for the repair CLI module.

State and dependencies: no state, persistence, or runtime dependencies.

Risks and test signals: the inaccurate wording is documentation drift only. Actual command behavior is covered by `LDBRepair` metadata and `TestLdbRepair`.
