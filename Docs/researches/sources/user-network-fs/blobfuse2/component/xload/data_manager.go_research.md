## sources/user-network-fs/blobfuse2/component/xload/data_manager.go

Purpose: Defines xload's remote data manager stage, responsible for moving chunk data between the remote `internal.Component` and splitter-owned blocks. Current implementation supports downloads only.

Important APIs and flow: `newRemoteDataManager` validates worker count, remote component, and stats manager, then initializes a `ThreadPool` with `Process`. `Start` and `Stop` manage that pool. `Process` respects item cancellation; when `Download` is true it calls `ReadData`, otherwise returns an unsupported-upload error. `ReadData` calls `remote.ReadInBuffer` with the work item's path, offset, destination buffer, and data length, then reports a `DATA_MANAGER` stats item.

State and dependencies: It embeds `XBase` for name, remote, stats, worker count, and thread pool. It depends on `internal.ReadInBufferOptions` and `StatsManager`.

Risks: Upload/sync modes are intentionally unsupported. `ReadData` passes the whole block buffer and file size as `Size`; remote implementations must use offset and buffer length correctly. Cancellation only prevents starting work; an in-flight `ReadInBuffer` is not interrupted. Tests cover construction validation and unsupported/cancelled process errors.
