# sources/test-tools/ior/src/aiori-MPIIO.c

## Purpose
Implements the IOR `MPIIO` backend with MPI file handles, optional MPI_Info hints, preallocation, explicit-offset transfers, collective I/O, and optional MPI file views/datatypes for strided patterns.

## Important APIs, Types, and Functions
- `mpiio_fd_t` stores `MPI_File` and derived datatypes for transfer/file views.
- `MPIIO_options` exposes hints file, show-hints, preallocate, use-strided-datatype, and use-file-view options.
- `MPIIO_Open` maps IOR flags to MPI modes, selects communicator, applies hints, opens/truncates, optionally preallocates, and creates datatypes/file views.
- Count-wrapper functions provide `MPI_Count` compatibility where native `_c` APIs are unavailable.
- `MPIIO_Xfer` selects read/write function pointers for independent/collective and explicit/file-view transfers, checks transferred bytes, and retries short noncollective transfers.
- `SeekOffset` converts absolute IOR offsets to file-view offsets.
- `MPIIO_GetFileSize`, `MPIIO_Access`, `MPIIO_Delete`, and `MPIIO_Fsync` provide shared helpers used by HDF5 and NCMPI.

## Control Flow
Parameter validation rejects unsupported or incompatible combinations such as shared file pointers, random offsets with collective I/O, and large file-view segments on small `MPI_Aint`. Open configures state based on `filePerProc`, `collective`, and file-view options. Transfer either calls explicit-offset `MPI_File_*_at[_all]` or sets/seeks a file view and uses individual file pointers.

## State and Persistence
Persistent state is the MPI-IO target file. Runtime state is global hints plus per-file MPI handles and datatypes. Fsync calls `MPI_File_sync`; close frees derived datatypes when file views were used.

## Dependencies and Integration Points
Requires MPI and IOR utility functions `SetHints`/`ShowHints`. Provides helpers referenced by HDF5 and NCMPI and registers POSIX metadata helpers for statfs/mkdir/rmdir/stat.

## Risks and Edge Cases
- `MPI_MODE_UNIQUE_OPEN` is always set, which assumes no concurrent non-MPI openers.
- Strided datatype mode overloads `length` as a segment count and can return a synthetic transfer size for skipped offsets.
- Collective short-transfer retry is intentionally disabled; caller must handle short byte counts.
- Shared file pointer code is present but rejected/unfinished.
- `MPIIO_Delete` ignores delete errors.

## Test Signals
Run independent and collective I/O, file-per-process and shared-file modes, hints show/pass-through, preallocation, truncation, file-view and strided-datatype options, short-transfer behavior, dry-run paths, and helper use from HDF5/NCMPI.
