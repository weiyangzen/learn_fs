## sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/keyvalue/interfaces/package-info.java

Purpose: Documents the interface package for key-value container block and chunk manager contracts.

Important APIs and functions: The package contains contracts such as `BlockManager` and `ChunkManager`, which are consumed by handlers, dispatchers, and container operations while implemented by layout-specific classes.

Control flow and state: No runtime logic appears in this file. It marks a boundary where container operations depend on abstract APIs instead of concrete storage layouts.

Persistence and dependencies: Persistence is indirect through implementations that write chunk files and RocksDB metadata. This file has no imports or direct runtime dependency.

Risks: If new contracts are added outside this package, handler code may become more tightly coupled to implementation classes. Documentation should continue to reflect the public surface of key-value container managers.

Test signals: Build and package-level documentation checks; behavioral testing belongs to the interfaces' implementors.
