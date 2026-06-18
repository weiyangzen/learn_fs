# sources/test-tools/crashmonkey/code/user_tools/api/wrapper.h

Purpose: central user-tool wrapper interface for filesystem operations. It abstracts raw POSIX/syscall functions behind `FsFns`, records mutations as `DiskMod` objects in `RecordCmFsOps`, and offers `PassthroughCmFsOps` for execution without recording.

Important APIs/types/functions: abstract `FsFns`, concrete `DefaultFsFns`, abstract `CmFsOps`, recording `RecordCmFsOps`, passthrough `PassthroughCmFsOps`, fd-to-path map `fd_map_`, mmap tracking map `mmap_map_`, `mods_`, `Serialize`, `CmOpenCommon`, and `WriteWhole`. The API covers mknod/mkdir/open/lseek/write/pwrite/mmap/msync/munmap/fallocate/close/rename/unlink/remove/fsync/fdatasync/sync/sync_file_range/checkpoint.

Control flow: callers use the `Cm*` interface. `RecordCmFsOps` forwards to `FsFns`, records relevant metadata/data into `DiskMod`, and serializes the mod stream; `PassthroughCmFsOps` simply delegates to `FsFns`. The header exposes protected internals for tests.

State/persistence behavior: records create, truncate, data, metadata, mmap, fallocate, fsync, sync, sync-file-range, and checkpoint intent, plus maps open descriptors to paths and writable shared mmaps to file ranges. Dependencies/integration: depends on POSIX headers and `DiskMod`; used by generated tests, harness code, and gtests.

Risks/test signals: the abstraction is broad and manually maintained; unsupported syscalls or direct syscalls in tests bypass recording. Tests in `CmFsOpsTest.cpp` cover many but not all operations, especially rename and fallocate corner cases.
