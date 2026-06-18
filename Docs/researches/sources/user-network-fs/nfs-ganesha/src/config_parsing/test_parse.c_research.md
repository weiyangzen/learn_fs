# sources/user-network-fs/nfs-ganesha/src/config_parsing/test_parse.c

## Purpose

`test_parse.c` is a small standalone parser smoke-test program that parses a supplied config file, frees it, then parses it again to exercise parser cleanup and reload behavior.

## Important APIs, Types, and Functions

The only function is `main`. It calls `config_ParseFile` and `config_Free` from the config parser API and exits with `EINVAL` on usage or parse failure.

## Control Flow

The program requires one file path argument, parses it, prints the returned pointer, fails if null, frees it, parses the same file again, prints the new pointer, fails if null, frees it, and exits success.

## State and Persistence Behavior

It allocates and frees two complete parse trees. It does not initialize `config_error_type` before passing it, which may reflect an older API or make diagnostics unsafe depending on the current function signature.

## Dependencies and Integration Points

It depends on `config_parsing.h` and the parser library. It is useful as a developer smoke test rather than a production binary.

## Risks and Edge Cases

The local `err_type` is uninitialized, so if `config_ParseFile` expects `err_type->fp` to be valid, this test can produce undefined behavior on errors. Output lacks newlines, and usage errors call `exit(EINVAL)` after printing to stdout.

## Test Signals

Build and run against valid, invalid, include-heavy, and URL-free configs. Memory checking across the parse/free/parse/free cycle is the main value of this test.
