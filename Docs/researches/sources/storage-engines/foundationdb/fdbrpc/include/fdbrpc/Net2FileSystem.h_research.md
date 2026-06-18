## sources/storage-engines/foundationdb/fdbrpc/include/fdbrpc/Net2FileSystem.h

Purpose: Declares the production asynchronous file system implementation backed by Net2/IAsyncFile primitives.

Important APIs/types/functions: `Net2FileSystem final : IAsyncFileSystem` overrides `open`, `deleteFile`, `lastWriteTime`, and `renameFile`; exposes static `stop()` and `newFileSystem()` helpers; and optionally exposes actor lineage sampling state.

Control flow: Implementations are elsewhere. Constructors accept an IO timeout and optional file-system path list/string; Linux builds store device IDs and a `checkFileSystem` flag for path/device validation.

State and persistence behavior: The object owns runtime file-system configuration and optional Linux device-id tracking. File methods operate on actual host files and therefore affect durable filesystem state through their implementations.

Dependencies and integration points: Depends on `flow/IAsyncFile.h` and is used where the network layer installs the process-global async file system. It is the production counterpart to simulator file systems.

Risks: Durable delete and rename semantics depend on implementation details outside the header. Linux device checks can reject or classify paths if device IDs are wrong. Static global install/stop APIs can affect all async file users in a process.

Test signals: File open/read/write, durable delete, rename, last-write-time, timeout behavior, multi-path configuration, Linux device-check behavior, and sampling lineage exposure.
