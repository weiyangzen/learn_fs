# File Research: sources/virtualization/nbdkit/server/fuzzer.c

Purpose: Provides a libFuzzer harness for the nbdkit server, compiled only when `ENABLE_LIBFUZZER` is enabled.

Entry point:
- `LLVMFuzzerTestOneInput(data, size)` creates a Unix socketpair and forks.
- Parent runs the nbdkit server side.
- Child acts as a synthetic NBD client feeding fuzz input.

Server side:
- Calls the renamed normal `main` function, `fuzzer_main`.
- Runs nbdkit with `-s`, `--log=null`, and the in-tree memory plugin with a `1M` size.
- Temporarily dup2s the socket over stdin/stdout so the normal `-s` path processes the fuzzed connection.
- Restores original stdin/stdout after `fuzzer_main`.

Client side:
- Polls the socket for read/write readiness.
- Writes remaining fuzz data when possible.
- Reads and discards server output.
- Shuts down the write side once all fuzz data is sent.

Error handling:
- Parent waits for the child and prints a diagnostic for nonzero/bad exit status.
- Many client read/write failures are treated as normal fuzzing termination rather than harness failure.
