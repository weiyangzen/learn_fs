# sources/storage-engines/sqlite/ext/wasm/SQLTester/touint8array.c

## Purpose

This tiny C utility converts stdin bytes into a JavaScript array literal of decimal byte values. It is used by `SQLTester/GNUmakefile` to embed `.test` files into `test-list.mjs` as `Uint8Array`-compatible content.

## Important Functions

The only function is `main()`. It reads stdin with `fgetc()`, prints an opening `[`, prints each byte as an unsigned decimal-style integer separated by commas, inserts a newline every 30 bytes for readability, prints the closing `]`, and returns zero.

## Control Flow

The program initializes a byte counter, return code, column width, and current character. It loops until `fgetc(stdin)` returns `EOF`. For each byte, it emits a comma unless this is the first value, emits a newline at each `colWidth` boundary, and prints the byte value. There is no option parsing and command-line arguments are ignored.

## State and Persistence

The utility maintains only local process state and writes all output to stdout. It creates no files itself. Persistence is provided by the makefile redirecting stdout into `test-list.mjs`.

## Dependencies and Integration Points

It depends only on the C standard I/O header. It is compiled by `SQLTester/GNUmakefile` into `./touint8array` and used in a shell loop over sorted test files. Its output is embedded directly into JavaScript object literals consumed by `SQLTester.run.mjs` and `SQLTester.mjs`.

## Risks and Edge Cases

The code uses `int ch` so it can distinguish all byte values from `EOF`. It prints byte values as `%d`, which is valid for the `fgetc()` result range. It does not report read errors separately from EOF, does not escape or annotate data, and does not wrap output in `new Uint8Array(...)`; callers must use it in a context where a plain array is acceptable. Extremely large inputs produce very large decimal-text output.

## Test Signals

A simple signal is that piping any file through the utility yields syntactically valid bracketed comma-separated numbers. The makefile's successful generation of `test-list.mjs` and subsequent import by `SQLTester.run.mjs` validates integration.
