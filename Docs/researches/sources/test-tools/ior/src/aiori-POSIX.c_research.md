# sources/test-tools/ior/src/aiori-POSIX.c

## Purpose
Implements the primary POSIX IOR backend, including open/create/read/write/close/delete/sync, direct I/O, optional Lustre/BeeGFS/GPFS/GPU Direct tuning, range locks, and mdtest metadata integration.

## Important APIs, Types, and Functions
- `posix_fd` wraps a POSIX fd and optional `CUfileHandle_t`.
- `posix_options_t` is defined in `aiori-POSIX.h` and includes direct I/O, Lustre striping/pool, GPFS hints, BeeGFS striping, GPU Direct, and range lock controls.
- `POSIX_options` exposes command-line options conditionally by compile-time feature macros.
- `POSIX_check_params` validates BeeGFS chunk size, Lustre pool/stripe combinations, and GPU Direct requirements.
- `POSIX_Create` maps options to `open64`, `llapi_file_open*`, Lustre ioctl striping, BeeGFS file creation, GPFS hints, and GPU Direct registration.
- `POSIX_Open` opens existing files with requested access and optional tuning.
- `POSIX_Xfer` performs seek, optional range lock, read/write or cuFileRead/cuFileWrite loops, short-transfer retry logic, fsync-per-write, and GPFS access hints.
- `POSIX_Fsync`, `POSIX_Sync`, `POSIX_Close`, `POSIX_Delete`, `POSIX_Rename`, and `POSIX_GetFileSize` provide lifecycle and metadata operations.

## Control Flow
IOR initializes/finalizes GPU Direct driver when compiled. Create has specialized paths for Lustre striping and BeeGFS file creation before falling back to `open64(O_CREAT|O_RDWR)`. Shared-file Lustre creation uses MPI barriers so rank 0 creates/stripes before other ranks open. Transfers seek to the requested offset and loop until all bytes are moved or retry limits/short reads stop progress.

## State and Persistence
Persistent state is the POSIX-visible filesystem. Runtime state is global hints plus per-open `posix_fd`. Durability is through `fsync` or `system("sync")`. Optional GPFS/Lustre/BeeGFS/GPU Direct settings affect filesystem/client behavior rather than IOR-owned persistent metadata.

## Dependencies and Integration Points
Requires POSIX, optional GPFS headers, BeeGFS headers, Lustre user/API headers, CUDA/cuFile, MPI, and IOR utility helpers. Other backends reuse POSIX helpers directly, notably MMAP, PMDK metadata, HDF5 metadata, MPIIO metadata, and NCMPI metadata.

## Risks and Edge Cases
- `POSIX_Fsync` casts the argument to `posix_fd *`, but `POSIX_Xfer` passes `&fd` when fsync-per-write is set; that is a type mismatch risk.
- `system("sync")` is global and shell-dependent.
- Range locks are released only after the transfer loop; early returns on read/write errors can skip unlock and GPFS access-end hints.
- Feature-specific paths are compile-time-dependent and hard to cover in one build.
- GPU Direct errors are warned during handle registration but later transfer paths may still try cuFile operations.

## Test Signals
Test basic POSIX read/write/delete/rename/stat, dry-run, direct I/O alignment, fsync-per-write, short read/write behavior, range locks including error paths, Lustre/BeeGFS/GPFS feature builds, GPU Direct builds, shared-file creation barriers, and helper callers such as MMAP/HDF5/MPIIO/NCMPI.
