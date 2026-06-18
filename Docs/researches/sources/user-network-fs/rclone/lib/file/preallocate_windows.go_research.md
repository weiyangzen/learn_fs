# sources/user-network-fs/rclone/lib/file/preallocate_windows.go

Source read signal: reviewed complete local file (105 lines, sha256 d65b3007c15d1f8b).

Purpose: Windows implementation of preallocation and sparse-file marking using NT and DeviceIoControl APIs.

Important APIs/types/functions: Defines lazy `ntdll` procs, structs matching native info layouts, `PreallocateImplemented=true`, `PreAllocate`, `SetSparseImplemented=true`, and `SetSparse`.

Control flow: `PreAllocate` queries volume allocation-unit sizes, rounds requested size up to cluster size, calls `NtSetInformationFile` with `FileAllocationInformation`, and maps Windows disk-full handles to `ErrDiskFull`. `SetSparse` calls `DeviceIoControl` with `FSCTL_SET_SPARSE`.

State and persistence behavior: Alters allocation state of the supplied file and can mark it sparse. Package-level lazy procs and mutex are process state.

Dependencies and integration points: Uses `golang.org/x/sys/windows`, `syscall`, `unsafe`, `sync`, and `os`. Called by local write paths that want efficient allocation on NTFS-like filesystems.

Risks and test signals: Native struct layout and information-class constants must match Windows ABI. Cluster-size zero is guarded. Error mapping should be tested on full volumes and sparse-capable filesystems.
