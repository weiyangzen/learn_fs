# sources/user-network-fs/blobfuse2/common/util.go
## sources/user-network-fs/blobfuse2/common/util.go

Purpose: collects cross-cutting utilities for mount detection, filesystem cleanup, encryption, path expansion, disk usage, checksums, pipeline validation, flag formatting, and goroutine IDs.

Important APIs/functions: mount helpers `IsDirectoryMounted`, `IsMountActive`, `ListMountPoints`; filesystem helpers `IsDirectoryEmpty`, `TempCacheCleanup`, `DirectoryExists`, `WriteToFile`; identity/path helpers `GetCurrentUser`, `NormalizeObjectName`, `ExpandPath`, `NotifyMountToParent`; crypto/checksum helpers `EncryptData`, `DecryptData`, `GetCRC64`, `GetMD5`; system helpers `GetCurrentDistro`, `GetUsage`, `GetFuseMinorVersion`; concurrency helpers `BitMap64`, `KeyedMutex`, `GetGoroutineID`; pipeline helpers `ComponentInPipeline`, `ValidatePipeline`, `UpdatePipeline`, and `PrettyOpenFlags`.

Control flow: mount functions parse `/etc/mtab`, call `pidof`/`ps`, or shell out to system tools. AES-GCM helpers use the raw passphrase bytes as the AES key, prepend nonce to ciphertext, and split nonce/ciphertext on decrypt. `ExpandPath` handles `~/`, environment expansion, preserves Azure special `$web`/`$logs`/`$changefeed`, and returns an absolute path. `BitMap64` uses atomic CAS loops. Pipeline validation rejects mutually exclusive cache/xload components; update swaps cache components with xload/block-cache.

State and persistence: global booleans `RootMount`, `ForegroundMount`, `IsStream`, selected `du` path cache, and monitoring globals are mutated/read. Utilities may delete directory contents, write files, signal parent processes, or read system files.

Dependencies/integration: Linux `/etc/mtab`, `pidof`, `ps`, `du`, `fusermount3`, `/etc/os-release`, AES, CRC64/MD5, goid, ini parser, and syscall signals.

Risks: `DecryptData` slices `cipherData` before checking length, so too-short ciphertext can panic. `IsMountActive` uses substring matching on command line args, which can false-positive. `WriteToFile` defaults to `0777`. `UpdatePipeline` does not append missing components except replacement cases. Many helpers are Linux-specific.

Test signals: `util_test.go` covers atomic bitmap behavior, mount-active integration, directory existence/cleanup, encryption errors and round trip, path expansion, disk usage, checksums, pipeline validation/update, open flag formatting, goroutine ID behavior, and `SetFrsize`.
