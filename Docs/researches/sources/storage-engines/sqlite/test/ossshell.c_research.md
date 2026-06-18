# sources/storage-engines/sqlite/test/ossshell.c

## Purpose

`ossshell.c` is a local replay shell for `ossfuzz.c`. It reads files and passes their raw bytes to `LLVMFuzzerTestOneInput()`, allowing developers to reproduce OSS-Fuzz corpus entries or crashes outside OSS-Fuzz.

## Important APIs, Types, and Functions

It declares `LLVMFuzzerTestOneInput()` from `ossfuzz.c`, mirrors debug flag constants, declares `ossfuzz_set_debug_flags()`, and implements `main()`. Supported options are `--show-errors`, `--show-max-delay`, and `--sql-trace`.

## Control Flow

Arguments are scanned in order. Options update the debug mask and immediately call `ossfuzz_set_debug_flags()`. File arguments are opened, sized with `fseek()`/`ftell()`, read into a reusable `realloc()` buffer, and passed to the fuzz entry point. The shell prints `<filename>... ok` for each successful replay.

## State and Persistence Behavior

The shell persists no files. It reuses one heap buffer for inputs and leaves SQLite/fuzzer state management to `ossfuzz.c`. Debug flags remain active for later files once enabled.

## Dependencies and Integration Points

It links with `ossfuzz.c` and SQLite headers. It is used in local corpus replay, crash triage, and debug-output workflows.

## Risks and Test Signals

`--sql-trace` may be a stub because `ossfuzz.c` does not visibly install a trace callback. Zero-length files and huge files are only guarded by allocation/read behavior. Signals are `ok` per file, non-zero exit for unreadable/read-error files, and any crash or diagnostic from the fuzz target.
