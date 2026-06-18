# sources/storage-engines/wiredtiger/tools/xray_to_optrack/xray_to_optrack.cpp Research

## Purpose

`xray_to_optrack.cpp` converts an LLVM XRay trace plus instrumentation map into one OpTrack log file per thread. Each output record is a line of `record_type function_name tsc`, where enter events map to `0` and exit/tail-exit events map to `1`.

## Important APIs, Types, and Functions

The implementation lives in namespace `xray_to_optrack`. `make_error()` creates LLVM `StringError` values. `xray_to_optrack_record_type()` maps `llvm::xray::RecordTypes` to OpTrack integer record types and rejects unsupported XRay record kinds. `write_optrack_record()` writes one line to an output stream. `symbolize_func_id()` maps an XRay function id to a full symbol name using an instrumentation map address table, `llvm::symbolize::LLVMSymbolizer`, and a `llvm::DenseMap<uint32_t, std::string>` cache. `generate_optrack_log_name()` constructs `optrack_<pid>_<tid>`. The central `xray_to_optrack(instr_map, input)` loads the LLVM instrumentation map and trace file, opens per-thread output streams, symbolizes each record, and writes converted records. `main()` validates two arguments and prints LLVM errors.

## Control Flow

The converter loads the map first, then the trace. It iterates every `llvm::xray::XRayRecord`, lazily opens an output file keyed by `record.TId`, converts the record type, resolves the function name, and appends a line with the record TSC. Errors short-circuit through LLVM `Error`/`Expected` values and cause `main()` to return failure.

## State and Persistence Behavior

The tool writes output files named only by process id and thread id in the current working directory. It maintains an in-memory symbol cache and output-file map for the life of the process. It does not append explicitly; default `std::ofstream` construction truncates any existing file with the same name.

## Dependencies and Integration Points

It depends on LLVM XRay trace/instrumentation APIs, LLVM symbolization, DenseMap, and standard file streams. Its output format is the integration point with WiredTiger OpTrack consumers. It expects the instrumentation map path to be symbolizable by LLVM against the addresses returned by `map->getFunctionAddresses()`.

## Risks and Edge Cases

Files are keyed only by thread id in the `files` map, so if a trace contains the same TID under multiple PIDs, records would share one stream even though the filename includes the PID from the first record. Existing `optrack_*` files can be overwritten. Unsupported XRay record types abort the whole conversion. Symbol names containing whitespace are written unescaped, which may matter to downstream parsers expecting space-separated fields. The error output streams `llvm::Error` directly; compatibility depends on LLVM's raw_ostream operator overloads.

## Test Signals

Tests should use a small synthetic XRay trace/instrumentation map with enter, exit, and tail-exit records, verify per-thread output names and line format, exercise missing function ids and invalid symbols, and check overwrite/current-directory behavior.
