# sources/storage-engines/foundationdb/fdbserver/kvstore/include/fdbserver/kvstore/KVFileUtils.h

## Purpose
This header declares standalone utilities for kvstore file diagnostics: checksum-file generation, consistency/integrity checking, and dumping contents.

## Important APIs, Types, And Functions
`GenerateIOLogChecksumFile(std::string filename)` writes or derives checksum metadata for an IO log file. `KVFileCheck(std::string filename, bool integrity)` returns a `Future<Void>` for asynchronous checking, with the boolean selecting deeper integrity behavior. `KVFileDump(std::string filename)` asynchronously dumps a kvstore file.

## Control Flow
Callers pass a filename and await the returned Flow futures for check/dump operations. The checksum helper is synchronous by signature.

## State And Persistence Behavior
The functions operate on local files and may create checksum sidecar data or emit diagnostic output. Exact mutation and output behavior are implementation-defined outside this header.

## Dependencies And Integration Points
It depends on Flow futures and is likely used by command-line tools, recovery utilities, or test helpers around SQLite/kvstore files.

## Risks And Test Signals
Diagnostics must avoid corrupting inspected files. Tests should cover missing files, corrupt files, checksum mismatches, integrity-on versus integrity-off checks, large files, and dump output stability.
