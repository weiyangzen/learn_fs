## sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/metadata/package-info.java

Purpose: Documents the datanode metadata package as the place where database structure and read/write access classes live.

Important APIs and functions: The package contains schema definitions, store implementations, table wrappers, codecs, delete transaction abstractions, and witnessed-container metadata DB classes.

Control flow and state: This file has no runtime behavior. It describes the package boundary for RocksDB metadata used by containers and datanode-level witnessed-container state.

Persistence and dependencies: Persistent behavior in the package covers container block metadata, counters, delete transactions, last-chunk records, finalized blocks, and witnessed container create info. This file itself has no imports.

Risks: Because this package owns multiple schema versions and upgrade compatibility, documentation should remain explicit that both DB structure and access helpers belong here.

Test signals: Package compile and documentation checks; schema/store/codec behavior is covered by the individual classes.
