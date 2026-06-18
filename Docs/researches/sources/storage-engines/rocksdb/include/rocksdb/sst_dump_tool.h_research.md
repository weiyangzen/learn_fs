# sources/storage-engines/rocksdb/include/rocksdb/sst_dump_tool.h

Purpose: This header declares the object-oriented entry point for the SST dump tool. The tool inspects or verifies SST files using RocksDB options.

Important APIs and types: `class SSTDumpTool` exposes `int Run(int argc, char const* const* argv, Options options = Options());`.

Control flow: Callers instantiate `SSTDumpTool` and pass command-line arguments plus optional `Options`. The implementation parses arguments and operates on SST files. The default argument constructs default RocksDB options when the caller does not supply custom comparator/table settings.

State and persistence behavior: The header defines no persistent state. The tool can read SST files and may produce output or verification statuses depending on implementation arguments; it should not be assumed to mutate DB state from this declaration alone.

Dependencies and integration points: It includes `rocksdb/options.h`, which lets the tool share comparator, Env, table factory, and checksum behavior with the DB or caller. It integrates with command-line binaries, tests, and support tooling.

Risks and edge cases: Running the dump tool with options that do not match the SST's comparator/table format can misinterpret keys or fail. The `Options` default construction pulls in a heavy option surface for a small tool declaration.

Test signals: Tests should invoke `Run()` against valid, corrupt, and option-mismatched SST files, validate exit codes, and verify checksum/table-property reporting.
