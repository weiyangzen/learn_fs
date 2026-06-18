# sources/storage-engines/foundationdb/bindings/c/test/mako/logger.hpp

## Purpose
Defines Mako's formatted logger with process/thread prefixes and verbosity filtering.

## Important APIs, types, and functions
Verbosity constants, process-kind aliases, and `Logger` methods `printWithLogLevel`, `error`, `info`, `warn`, `debug`, `imm`, `setVerbosity`, and `isFor` form the API.

## Control flow
Each call checks log level against verbosity, formats a prefix and message with `fmt`, then writes errors/immediate output to stderr and other enabled output to stdout.

## State and persistence behavior
Logger stores process kind, verbosity, process id, and thread id. It writes to process streams, not files.

## Dependencies and integration points
Depends on `fmt`, `process.hpp`, assertions, and standard I/O. Used by Mako main/stats/worker/admin contexts.

## Risks and test signals
Prefix correctness matters for multi-process diagnostics. Verbosity mistakes can hide expected warnings or flood output.
