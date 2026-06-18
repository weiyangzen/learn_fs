# sources/storage-engines/foundationdb/bindings/c/test/unit/trace_partial_file_suffix_test.cpp

## Purpose
`trace_partial_file_suffix_test.cpp` verifies that FDB trace files use a configured partial-file suffix while the network is running and that the suffix is removed on shutdown, including for a simulated stray partial file from an earlier crash.

## Important APIs, Types, and Functions
- `fdb_check` aborts on C API errors.
- `set_net_opt` wraps `fdb_network_set_option` for string options.
- `file_exists` checks file presence.
- `main` configures tracing, creates a simulated stray `.tmp` trace file, runs the network, opens a database to initialize logging, waits for a new trace file, stops the network, checks rename behavior, and removes files.

## Control Flow
The test selects the API version, builds a random file identifier, creates a fake trace file ending in `.tmp`, enables tracing and sets file identifier/suffix, starts the network, opens/destroys a database using `argv[1]`, loops over current-directory files until a real trace file appears with the suffix, stops the network, asserts both partial files were renamed without the suffix, then deletes them.

## State and Persistence Behavior
The test creates and deletes trace files in the current working directory. It does not intentionally mutate database contents, but it opens a database to trigger trace initialization.

## Dependencies and Integration Points
It uses the FDB C API, `flow/Platform.h` for directory listing, C++ file/thread/random utilities, and process current-directory trace behavior.

## Risks
The wait loop has no timeout and can hang if tracing does not create a file. It assumes `argv[1]` exists. File name matching is current-directory based and could collide, though the random identifier lowers risk. Assertions are active because `NDEBUG` is undefined.

## Test Signals
Success proves partial trace suffix configuration, startup trace creation, shutdown rename, stray partial-file cleanup, and cleanup deletion. Failure indicates trace lifecycle or file naming regression.
