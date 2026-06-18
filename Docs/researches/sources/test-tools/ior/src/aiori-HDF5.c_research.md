# sources/test-tools/ior/src/aiori-HDF5.c

## Purpose
Implements the IOR `HDF5` backend using parallel HDF5 over MPI-IO. It stores benchmark transfers in generated HDF5 datasets and maps IOR offsets to HDF5 hyperslabs.

## Important APIs, Types, and Functions
- `HDF5_options_t` embeds `mpiio_options_t` and adds collective metadata, individual dataset flag, no-fill, alignment, and dataset chunk-size options.
- `aiori_h5fd_t` stores HDF5 file id, transfer property list, dataset/data-space ids, and read-check/dataset lifecycle flags.
- `HDF5_Open` configures file creation/access property lists, MPI-IO hints, alignment, optional collective metadata, transfer mode, memory dataspace, and initial dataspace shape.
- `HDF5_Xfer` decides when to create/open the next dataset and performs `H5Dwrite` or `H5Dread`.
- `SetupDataSet` creates or opens dataset names like `Dataset-0000.0000`, applies chunking and no-fill options, and obtains file dataspace.
- `SeekOffset` maps IOR offsets into a one-dimensional hyperslab selection.
- Metadata helpers use native VOL checks where available and otherwise route to MPIIO/POSIX helpers.

## Control Flow
`HDF5_init_xfer_options` stores hints and also initializes MPIIO hints because HDF5 reuses MPIIO helpers. Create delegates to open. Open establishes the HDF5 file and memory transfer layout. Each xfer may roll to a new dataset at segment boundaries; read-check toggles avoid opening and closing the dataset twice for the two check passes. Close tears down dataset, dataspaces, transfer property list, file id, and wrapper.

## State and Persistence
Persistent data is the HDF5 file containing one or more generated datasets. Runtime state includes global hints, per-file HDF5 IDs, and a static dataset suffix in `SetupDataSet`. `HDF5_Fsync` calls `H5Fflush` with local scope. `HDF5_Finalize` calls `H5close`.

## Dependencies and Integration Points
Requires HDF5, MPI, IOR MPIIO helpers, POSIX metadata helpers, and optional HDF5 feature macros such as collective metadata, `H5Fdelete`, `H5Fis_accessible`, and VOL APIs.

## Risks and Edge Cases
- `individualDataSets` is rejected by `HDF5_check_params`, but dead code for it remains.
- Dataset suffix is static and reset only for newly opened files; concurrent/multiple handles could interact unexpectedly.
- `HDF5_Close` assumes dataset/file dataspace were created unless dry-run is set.
- Non-native VOL connectors lack statfs, mkdir, rmdir, stat, and file-size support in this backend.
- Error handling often calls `exit`, which can bypass MPI-coordinated shutdown.

## Test Signals
Run with parallel HDF5, independent and collective transfers, hints display, alignment/no-fill/chunk options, segment rollover producing multiple datasets, read-check double pass, native vs non-native VOL metadata helpers, and delete with and without `H5Fdelete`.
