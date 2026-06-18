# sources/storage-engines/foundationdb/fdbclient/S3Client_cli.cpp

## Purpose
`S3Client_cli.cpp` builds the standalone `s3client` executable around the library helpers in `S3Client.cpp`. It provides command-line `cp`, `ls`, and `rm` operations for FoundationDB `blobstore://` URLs, initializes the Flow network, TLS/blob credentials, knobs, proxy state, and optional tracing, then runs the selected asynchronous S3 operation to completion.

## Important APIs, types, and functions
The `s3client_cli` namespace defines SimpleOpt option IDs and the `Options[]` table for trace flags, blob credentials, TLS options, build flags, knobs, proxy, help, and recursive listing. `Params` is the parsed command model: proxy, tracing fields, `BackupTLSConfig`, knob overrides, source/target, command, URL-side marker, default integrity-check knob name, and `ls_recursive`.

`printUsage()` documents commands and URL format. `parseCommandLine()` validates command arity and whether source or target is a blobstore URL. `Params::updateKnobs()` adds `blobstore_enable_object_integrity_check=true` unless overridden, applies knob overrides with `setupClientKnobs()`, then reinitializes client knobs. `run()` dispatches to `copyUpDirectory`, `copyUpFile`, `copyDownDirectory`, `copyDownFile`, `deleteResource`, or `listFiles`. `main()` owns process setup and error-to-exit-code mapping.

## Control flow
`main()` reconstructs the command line for tracing, parses arguments with `CSimpleOpt`, prints usage on parse/build/help non-success, configures trace output if enabled, sets up TLS, calls `platformInit()`, `Error::init()`, and `setupNetwork()`, then applies knob updates. If no `--proxy` was passed, it reads `FDB_PROXY`; a valid proxy is stored in `g_network->global(INetwork::enProxy)` for `S3Client.cpp` endpoint construction.

After emitting a `ProgramStart` trace event and opening trace files, `main()` loads blob credentials, wraps `run(params)` in `stopAfter`, starts `runNetwork()`, and maps failed futures/exceptions to FoundationDB exit codes. `run()` chooses upload versus download based on which argument starts with `BLOBSTORE_PREFIX`; local directory tests are performed with `std::filesystem::is_directory`.

## State and persistence behavior
The CLI itself persists no database state. It mutates process-global runtime state: network options, trace-file settings, client knobs, TLS/blob-credential configuration, and the global proxy optional. The underlying command may write S3 objects, delete S3 resources, or write local files through the library helpers. Trace files are written when enabled.

## Dependencies and integration points
This executable is declared separately in `fdbclient/CMakeLists.txt` after removing `S3Client_cli.cpp` from library sources. It links Flow, fdbclient, TLS, SimpleOpt, and the S3 client implementation. Shell tests under `fdbclient/tests/s3client_test.sh`, backup test helpers, and bulkload tests invoke `bin/s3client`. The CLI accepts the same blob credential format as backup tooling through `BackupTLSConfig`.

## Risks and edge cases
`--help` and `--build-flags` return `FDB_EXIT_ERROR` after printing, so callers expecting zero for informational commands need to account for current behavior. The usage says `--recursive` is only valid with `ls`, but parsing does not reject it for other commands; it is simply ignored outside `ls`. If a blobstore source is copied to a non-directory target, the path is treated as a file target rather than forcing directory semantics. The default integrity-check knob is enabled by CLI policy, which can differ from library callers unless they set the knob explicitly. Proxy validation only accepts hostname or parsed network address strings.

## Test signals
`s3client_test.sh` is the main behavioral test: upload/download, directory copy, listing, recursive listing, errors for nonexistent resources, empty buckets, credentials, TLS CA handling, and integrity-check knob combinations. Build and smoke coverage also comes from CMake `s3client_test`, `gcs_client_test`, backup tests, and bulkload tests that shell out to the executable.
