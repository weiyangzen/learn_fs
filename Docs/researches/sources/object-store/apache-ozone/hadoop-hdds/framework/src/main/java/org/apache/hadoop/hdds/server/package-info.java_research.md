# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/server/package-info.java

Purpose: this package-info documents `org.apache.hadoop.hdds.server` as common server-side utilities for HDDS/Ozone server components.

Important APIs/types/functions: it only declares package-level Javadoc. Subpackages in this research group include `events` and `http`, which provide event dispatch and embedded web server support.

Control flow: none.

State and persistence: none.

Dependencies/integration: establishes the common server namespace used by SCM, OM, datanode, Recon, and shared framework code.

Risks: none directly.

Test signals: no direct tests needed; functionality is in concrete classes under subpackages.
