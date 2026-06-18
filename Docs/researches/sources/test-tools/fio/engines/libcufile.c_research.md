# sources/test-tools/fio/engines/libcufile.c

## Purpose
Implements fio's NVIDIA cuFile engine for GPU Direct Storage style I/O, with a second POSIX mode that simulates CUDA copy overhead around ordinary pread/pwrite. It allocates GPU memory, optionally registers it with cuFile, registers file handles, and completes all operations synchronously from `queue()`.

## Important APIs, Types, And Functions
`struct libcufile_options` stores colon-separated GPU IDs, selected CUDA I/O mode, GPU memory pointer, POSIX simulation buffer, selected GPU, total allocation size, and one-shot alignment log flags. `struct fio_libcufile_data` stores the cuFile descriptor and handle per file. Important functions include `fio_libcufile_find_gpu_id()`, `fio_libcufile_init()`, `fio_libcufile_pre_write()`, `fio_libcufile_post_read()`, `fio_libcufile_queue()`, `fio_libcufile_open_file()`, `fio_libcufile_close_file()`, `fio_libcufile_iomem_alloc()`, `fio_libcufile_iomem_free()`, and `fio_libcufile_cleanup()`.

## Control Flow
Initialization uses a global mutex-protected `running` count so the cuFile driver is opened once for the first active worker and closed by the last. Each thread chooses a GPU by subjob number modulo the `gpu_dev_ids` list and calls `cudaSetDevice()`. I/O memory allocation creates fio's CPU buffer, optional POSIX junk buffer, CUDA device memory, initializes it, and registers the GPU buffer with cuFile in cuFile mode. File open uses generic fio open plus `cuFileHandleRegister()`.

`queue` handles sync via `fsync()`/`fdatasync()`. Read/write compute a per-`io_u` GPU offset, warn once for non-4KiB cuFile alignment, perform verify-related host/device copies or POSIX simulation copies, then loop until cuFile or POSIX I/O transfers the requested length. Reads may copy GPU data back to the fio buffer for verification.

## State And Persistence
Per-thread option state owns GPU memory and tracking flags. Per-file engine data owns cuFile handles. Global driver state is process-wide and reference counted by active jobs. Persistent file changes occur via `cuFileWrite()` or POSIX `pwrite()`; sync operations call the host file descriptor sync APIs.

## Dependencies And Integration Points
Depends on NVIDIA cuFile, CUDA driver/runtime APIs, pthread mutexes, and fio memory/file hooks. It registers as `FIO_SYNCIO`, so fio sees every queue operation as completed immediately.

## Risks
GPU offsets are derived from `io_u->index * xfer_buflen`, so variable block sizes can make offset assumptions fragile. cuFile alignment warnings are non-fatal even though performance or API behavior may vary. Global driver lifetime assumes all users of this engine follow the same process-local counter. Error handling mixes CUDA, cuFile negative statuses, and errno. POSIX mode intentionally copies through GPU memory but still writes from the fio CPU buffer.

## Test Signals
Test cuFile and POSIX modes, multiple GPU IDs/subjobs, verify and non-verify read/write, unaligned buffer lengths and offsets, partial cuFile/POSIX transfers, file handle register/deregister failures, CUDA allocation/register failures, sync/datasync operations, and last-thread driver close.
