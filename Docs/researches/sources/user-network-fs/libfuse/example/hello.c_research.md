# sources/user-network-fs/libfuse/example/hello.c

## Purpose

`hello.c` is the minimal high-level libfuse filesystem example. It exposes a root directory and one read-only file whose name and contents are configurable through command-line options. The source was read as a complete 184-line file.

## Important APIs, Types, and Functions

Callbacks in `hello_oper` are `hello_init`, `hello_getattr`, `hello_readdir`, `hello_open`, and `hello_read`. Option parsing uses `struct options`, `option_spec`, `fuse_opt_parse`, and `show_help`.

## Control Flow

`main` sets default duplicated strings, parses options, optionally appends `--help`, and calls `fuse_main`. FUSE invokes path-based callbacks: `getattr` returns directory or file metadata, `readdir` emits `.`, `..`, and the configured file, `open` enforces read-only access, and `read` slices the configured content by offset/size.

## State and Persistence Behavior

State is the static `options` struct and kernel cache settings. `hello_init` enables `kernel_cache` and toggles an async-read feature flag as an API demonstration. No data is persisted.

## Dependencies and Integration Points

It depends on the high-level `fuse.h` API and demonstrates option parsing via `fuse_opt`.

## Risks and Edge Cases

Callbacks compare `path + 1` without checking that the path is at least `/x`, which is normal for FUSE paths but still assumption-based. The filesystem is read-only and cannot reflect runtime option changes. Defaults are heap allocated so `fuse_opt_parse` can replace/free them.

## Test Signals

Mount, list root, stat/read the configured file, verify non-existent paths return ENOENT, write opens return EACCES, custom `--name` and `--contents` work, and help output preserves FUSE help behavior.
