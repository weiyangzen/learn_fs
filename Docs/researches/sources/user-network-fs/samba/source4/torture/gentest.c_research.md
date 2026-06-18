# sources/user-network-fs/samba/source4/torture/gentest.c

## Purpose
`gentest.c` is a differential SMB/SMB2 torture generator. It connects to two UNC shares, executes the same seeded sequence of randomly generated file operations against both servers, and fails when statuses, metadata, oplock behavior, or change notifications diverge outside configured ignore patterns.

## Important APIs, Types, and Functions
Global `options` controls protocol (`smb2`), seed, operation count, oplock use, ignored differences, preset seed replay, reconnect strategy, cleanup, and valid-only field generation. `servers[NSERVERS]` stores two test targets, each with two connection instances. `open_handles` maps local handle slots to corresponding SMB1 fnums or SMB2 handles on both servers. `op_parms` stores per-operation seeds and disabled flags for replay/backtracking. `current_op` records the active operation name, seed, status, talloc context, op index, and mismatch label.

Connection and state helpers include `connect_servers()`, `connect_servers_fast()`, `time_skew()`, handle mapping/add/remove functions, `wipe_files()`, and `dump_seeds()`. Random generators cover filenames, patterns, offsets, counts, access masks, create options, attributes, timestamps, EAs, security descriptors, locks, and reserved fields. SMB1 handlers include open/openx/ntcreatex, close, unlink, mkdir/rmdir, rename/ntrename, seek, readx/writex, lockingx, qpathinfo/qfileinfo, spathinfo/sfileinfo, and change notify. SMB2 handlers include create, close, read, write, lock, flush, echo, qfileinfo, and sfileinfo.

The macros `GEN_COPY_PARM`, `GEN_CALL`, `GEN_CALL_SMB`, `GEN_CALL_SMB2`, handle translation macros, and `CHECK_*` comparison macros are central. They clone generated parameters to both servers, translate local handles to each server's real handle, execute the protocol call, compare NTSTATUS values, check async side effects, and compare selected output fields.

## Control Flow
`main()` initializes Samba command-line support, parses two UNC targets and options, loads credentials, splits UNC names, initializes events and GENSEC, and calls `start_gentest()`. `start_gentest()` allocates handle and seed arrays, loads preset seeds or generates deterministic seeds from `options.seed`, then calls `run_test()`. `run_test()` connects/reconnects, writes seeds, wipes the `gentest` tree unless disabled, resets open handle state and operation counters, and loops over `options.numops`.

For each operation, `run_test()` seeds the PRNG with that operation's stored seed, picks an instance and an operation matching the selected protocol and ignore list, creates an operation talloc context, invokes the handler, records success counts, and stops on first mismatch. If analysis is enabled, `backtrack_analyze()` repeatedly disables chunks of operations and reruns the test to shrink the reproducer while preserving the same mismatch class. `analysecontinuous` keeps rerunning until failure.

## State and Persistence Behavior
The program deliberately mutates remote shares under a `gentest` directory: it creates, deletes, renames, writes, locks, changes metadata, creates EAs/security descriptors, and may leave files if `--skip-cleanup` is set or the process aborts. It persists a seed file through atomic `seeds.tmp` rename when `--seedsfile` is configured, enabling replay. Runtime state is mostly global and deterministic per operation seed, which is essential for reproducing failures and backtracking.

## Dependencies and Integration Points
The file uses Samba client raw SMB1 APIs, SMB2 APIs, event handling, credentials, GENSEC, loadparm, resolver configuration, security descriptor helpers, popt command-line support, and utility file loading. It is a standalone torture executable/tool rather than a suite registration file, and it integrates with real SMB servers via UNC paths and credentials.

## Risks
This tool is intentionally destructive to the target `gentest` tree and should run only against disposable shares. Differential comparison can produce false positives for legitimate server differences such as timestamp skew, indexing attributes, unsupported EAs/ACLs, or ignored status mappings; options like `--maskindexing`, `--noeas`, `--noacls`, and ignore files mitigate this. Global mutable state and async oplock/notify paths make replay sensitive to timing. Some SMB2 async processing is stubbed/commented, and SMB2 oplock/notify coverage is explicitly incomplete.

## Test Signals
Primary success is completing all generated operations with no unignored divergence and printing per-operation success counts. Failure reports include operation number, operation name, mismatched NTSTATUS or field, and current seeds. Seed dumping and backtracking provide reproducible minimized sequences for protocol or server behavior bugs.
