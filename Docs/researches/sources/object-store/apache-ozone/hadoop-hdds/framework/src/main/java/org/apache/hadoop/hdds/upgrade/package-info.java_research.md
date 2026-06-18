# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/upgrade/package-info.java

Purpose: this package-info documents `org.apache.hadoop.hdds.upgrade` as containing SCM upgrade-related classes.

Important APIs/types/functions: no runtime API is declared here. In this package, `HDDSLayoutVersionManager`, layout features, and upgrade actions coordinate HDDS storage layout upgrades/finalization.

Control flow: none in this file.

State and persistence: none.

Dependencies/integration: package integrates with the broader Ozone upgrade framework and SCM/datanode startup/finalization flows.

Risks: none directly.

Test signals: upgrade package behavior is covered by layout-version manager and SCM/datanode finalization tests.
