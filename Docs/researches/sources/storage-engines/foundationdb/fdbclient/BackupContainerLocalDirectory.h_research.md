# sources/storage-engines/foundationdb/fdbclient/BackupContainerLocalDirectory.h

Purpose: This header declares the local-filesystem `BackupContainerFileSystem` implementation for `file://` backup URLs. It is the factory-visible contract for local backup containers.

Important APIs and types: `BackupContainerLocalDirectory` inherits from `BackupContainerFileSystem` and `ReferenceCounted<BackupContainerLocalDirectory>`. It declares reference-count overrides, static `getURLFormat`, the constructor taking a URL plus optional encryption key and block size, static `listURLs`, and final overrides for `create`, `exists`, `readFile`, `writeFile`, `writeEntireFile`, `deleteFile`, `listFiles`, and `deleteContainer`. Its only direct data member is `std::string m_path`.

Control flow: The header keeps all implementation details in the `.cpp`; callers use it through `IBackupContainer` or `BackupContainerFileSystem` references. Static URL helpers let the shared factory advertise and discover local backup containers.

State and persistence behavior: `m_path` is the root of all persistent state for the container. Existence is defined as directory existence, while file-level format, metadata properties, encryption metadata, and backup manifests are inherited from the common filesystem layer.

Dependencies and integration points: It includes `BackupContainerFileSystem.h` and Flow futures/reference counting. It is included by `BackupContainer.cpp` and `BackupContainerFileSystem.cpp` for factory dispatch and tests.

Risks: Since the class exposes only a root path and filesystem operations, safety depends on constructor validation and the `.cpp` delete guard. Any new method must preserve the common container contract, especially relative paths, encryption setup, and source-tree-style path listing.

Test signals: Compile-time use verifies that local containers satisfy all abstract `BackupContainerFileSystem` methods. Runtime behavior is covered by `/backup/containers/localdir/*` tests and shared backup container tests.
