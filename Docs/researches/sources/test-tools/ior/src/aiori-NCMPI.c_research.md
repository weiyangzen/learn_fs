# sources/test-tools/ior/src/aiori-NCMPI.c

## Purpose
Implements the IOR `NCMPI` backend for Parallel NetCDF, storing IOR transfers in a NetCDF variable and using MPI-IO helpers for file size and access checks.

## Important APIs, Types, and Functions
- `ncmpi_options_t` embeds `mpiio_options_t` and tracks runtime `var_id`, `firstReadCheck`, and `startDataSet`.
- `NCMPI_options` exposes MPI-IO-like hints/preallocate/file-view options.
- `NCMPI_Create` and `NCMPI_Open` call `ncmpi_create`/`ncmpi_open` over `testComm`.
- `NCMPI_Xfer` defines dimensions and variable `data_var`, switches independent data mode when needed, maps offsets to `[segment][transfer][byte]`, and uses collective or independent vara calls.
- `GetFileMode` maps IOR flags to NetCDF flags and enables `NC_64BIT_DATA`.
- `NCMPI_GetFileSize` and `NCMPI_Access` delegate to MPIIO helpers.

## Control Flow
Hints are forwarded to MPIIO via `NCMPI_xfer_hints`. On the first write at a segment start, the backend defines dimensions and `data_var`, ends define mode, and stores the variable id. Reads look up the same variable. Each transfer computes segment and transfer indices from the absolute IOR offset.

## State and Persistence
Persistent state is a Parallel NetCDF file with an unlimited segment dimension and `data_var`. Runtime state lives partly in the options object (`var_id` and read-check toggles), plus a heap-allocated integer NetCDF file id.

## Dependencies and Integration Points
Requires PnetCDF, MPI, MPIIO helper functions, and POSIX metadata helpers. It registers no explicit `check_params`, so incompatible MPIIO-style options may not be validated here.

## Risks and Edge Cases
- Runtime dataset state is stored in backend options, which can conflict across multiple simultaneously open files.
- Options for preallocate/useFileView/useStridedDatatype are exposed but not applied by NCMPI transfer logic.
- `offsets[0]` uses `rank`, not `(rank + rankOffset) % numTasks`, while segment-position checks use rank offset.
- Independent mode begins but there is no explicit matching end before close in this file.

## Test Signals
Test file creation/open, collective and independent transfers, read-check toggling, rank-offset layouts, file-size/access delegation, large variable support, hints display, and multiple open files using separate option instances.
