# sources/test-tools/ior/src/ior.c

## Purpose
Contains the core IOR benchmark engine. It initializes MPI/test state, selects and initializes AIORI backends, validates parameters, generates file names and data patterns, executes write/read/check loops, times operations, reduces metrics, verifies data, removes files, and reports summaries.

## Important APIs, Types, And Functions
Exports `ior_run`, `ior_main`, `init_IOR_Param_t`, `AllocResults`, `FreeResults`, `CreateTest`, `GetPlatformName`, `GetTestFileName`, `test_time_elapsed`, and `GetOffsetArrayRandom`. Important internal functions include `test_initialize`, `test_finalize`, `ior_set_xfer_hints`, `InitTests`, `ValidateTests`, `TestIoSys`, `WriteOrRead`, `WriteOrReadSingle`, `CheckFileSize`, `CompareData`, `CountErrors`, `ReduceIterResults`, `RemoveFile`, `PrependDir`, `DistributeHints`, `HogMemory`, `StoreRankInformation`, and `ProcessIterResults`.

## Control Flow
`ior_main` initializes MPI, parses tests, initializes defaults, prints headers, runs each test, prints summaries, finalizes MPI, and destroys tests. `ior_run` provides a library-style variant using an existing communicator/output stream. For each test, `test_initialize` builds a smaller test communicator, sets globals, optionally initializes CUDA/backend, sends xfer hints, and prints start data. `TestIoSys` loops repetitions: setup buffers, warn on existing files, optionally remove old files, create/open backend fd, call `WriteOrRead`, close, check size, reduce/tally results, optionally verify data, read, remove files, and print summaries. `WriteOrRead` computes sequential or random offsets, handles stonewalling and min/max duration behavior, performs optional random prefill, and calls `WriteOrReadSingle` per transfer.

## State And Persistence Behavior
File-scope state includes `totalErrorCount` and selected `backend`; shared globals include `rank`, `rankOffset`, `testComm`, output streams, verbosity, and backend warning policy. Persistent benchmark artifacts are created through backend hooks and optionally removed unless `keepFile` or `keepFileWithError` applies. Optional CSV output is written per operation/rank and for rank details. Stonewalling can persist iteration counts in a status file.

## Dependencies And Integration Points
Depends on MPI, optional CUDA, AIORI backends, parser code (`parse_options.h`), utilities for timing, memory patterns, node mapping, aligned buffers, random functions, stonewalling storage, and output functions from `ior-output.c`. Every backend must honor the `ior_aiori_t` lifecycle and `xfer` byte-count contract used here.

## Risks And Edge Cases
Global `backend` and `testComm` make concurrent embedded runs unsafe. `test_finalize` frees global `testComm` rather than `test->params.testComm` by address, so global state must remain consistent. `CreateTest` shallow-copies `IOR_param_t`, including pointer fields and backend options, which complicates ownership. Random offset mode `>1` computes offsets using `sizerand / blockSize * blockSize - transferSize`, which can underflow for small sizes. Some buffers for `PrependDir` are heap allocated and returned without clear ownership at call sites. `WriteOrReadSingle` aborts on any short transfer, so async/object backends must accurately return byte counts. Parameter validation has backend-specific exclusions that may miss newer S3 backends in fsync warnings.

## Test Signals
Coverage should include write, read, write-check, read-check, file-per-process, shared-file, random offset modes, reorder modes, stonewalling/wear-out, min/max duration, GPU memory flags where available, save-per-op/rank CSV output, multi-repetition summaries, and every enabled backend's create/xfer/close/get_file_size/remove path.
