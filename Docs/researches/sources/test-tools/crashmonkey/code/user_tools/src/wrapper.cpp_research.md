# sources/test-tools/crashmonkey/code/user_tools/src/wrapper.cpp

Purpose: implementation of the filesystem operation abstraction declared in `wrapper.h`. It both delegates raw filesystem operations and records an ordered stream of logical `DiskMod` objects used by CrashMonkey replay and analysis.

Important APIs/types/functions: `DefaultFsFns` syscall wrappers, `RecordCmFsOps` recording methods, `PassthroughCmFsOps`, `CmOpenCommon`, `CmWrite`, `CmPwrite`, `CmMmap`, `CmMsync`, `CmFallocate`, `CmFsync`, `CmSync`, `CmSyncFileRange`, `CmCheckpoint`, `Serialize`, and helper `WriteWhole`. Recording uses `DiskMod::ModType` and `ModOpts`.

Control flow: `DefaultFsFns` maps methods to POSIX syscalls and checkpoint IPC. `RecordCmFsOps` records creates/truncates on open, captures write data and file-extension metadata, tracks writable shared mmaps and records msync ranges, classifies fallocate mode flags, records sync/fsync/checkpoint operations, and serializes mods. `PassthroughCmFsOps` forwards each operation without updating maps or mods.

State/persistence behavior: stateful members are fd-to-path mappings, mmap address mappings, and the accumulated mod vector. The serialized mod stream encodes the intended user-level operation order, while actual disk state is still governed by the filesystem and kernel.

Dependencies/integration: depends on Linux/POSIX syscalls, `DiskMod`, `actions.cpp` checkpoint IPC, and gtest coverage in `CmFsOpsTest.cpp`. Risks/test signals: rename only updates fd maps and does not append a `DiskMod`; `CmPwrite` contains unreachable code after return; `PassthroughCmFsOps::CmSyncFileRange` has no explicit return; direct syscalls by workloads bypass recording.
