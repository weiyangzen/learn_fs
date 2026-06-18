# sources/test-tools/ior/src/ior.h

## Purpose
Defines the public core data structures and entry points for the IOR benchmark engine. It describes test parameters, transfer buffers, per-operation results, test list nodes, and the callable main/run APIs.

## Important APIs, Types, And Functions
Defines `IOR_io_buffers`, `IOR_param_t`, `IOR_point_t`, `IOR_results_t`, and `IOR_test_t`. Declares `CreateTest`, `AllocResults`, `GetPlatformName`, `init_IOR_Param_t`, `ior_run`, and `ior_main`. Also defines `ISPOWEROFTWO` and HDFS placeholder types when HDFS support is disabled.

## Control Flow
`IOR_param_t` is populated from defaults and command-line/script parsing, then consumed by `ior.c` to drive backend selection, MPI communicator setup, file naming, data layout, timing, verification, and output. `IOR_results_t` arrays are allocated per test and filled per repetition.

## State And Persistence Behavior
The header itself owns no storage, but `IOR_param_t` carries almost all mutable test state: backend pointer/options, file names, MPI communicators, access mode flags, size/layout controls, random/stonewalling state, output paths, GPU memory settings, POSIX flags, URI, and transfer hints.

## Dependencies And Integration Points
Includes config, HDFS type definitions, `option.h`, `iordef.h`, `aiori.h`, MPI, and MPI-IO when needed. Comments explicitly require synchronized updates to defaults, usage, parser directives, and user guide whenever `IOR_param_t` changes.

## Risks And Edge Cases
`IOR_param_t` is large and shallow-copied in `CreateTest`, so pointer ownership is subtle. Adding fields without updating initialization/parsing/output documentation can produce uninitialized behavior. MPI communicator fields and backend options tie this structure to a specific runtime context. Some fields are intermediate parser strings, while others are authoritative runtime values.

## Test Signals
Builds with and without optional HDFS/MPI-IO support, parser/default round-trip tests, multi-test scripts, `ior_run` embedding tests, and result allocation/freeing validate this API.
