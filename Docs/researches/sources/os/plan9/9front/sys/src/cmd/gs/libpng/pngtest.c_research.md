# File Research: sources/os/plan9/9front/sys/src/cmd/gs/libpng/pngtest.c

This is libpng’s standalone test program. It reads a PNG, writes it back out through libpng, then byte-compares the original and generated files. It validates core chunk handling, row filtering, compression/decompression, metadata copying, optional user transforms, stdio-free I/O hooks, and debug memory hooks. It is not filesystem implementation code, though it performs normal host file I/O for testing.

Major responsibilities:
- Provide `main` command-line handling for single-file and multi-file test modes.
- Implement `test_one_file`, the main read-copy-write-compare workflow.
- Register optional row status callbacks: `read_row_callback`, `write_row_callback`.
- Register optional user transform callbacks: `count_filters` and `count_zero_samples`.
- Provide stdio-free read/write/flush/error shims when `PNG_NO_STDIO` is enabled.
- Provide debug allocation tracking through `png_debug_malloc` and `png_debug_free` when `PNG_USER_MEM_SUPPORTED && PNG_DEBUG`.
- Print version, memory, filter, tIME, and pass/fail diagnostics.

Control flow and data flow:
- `main` parses `-m`, `-v`, `-mv`, input, and optional output file names.
- `test_one_file` opens input/output files, creates read/write structs and info structs, sets `setjmp` handlers, initializes I/O, configures callbacks, and preserves unknown chunks according to compile-time support.
- It reads input metadata with `png_read_info`, retrieves each supported chunk using `png_get_*`, and stores it in the write info struct using corresponding `png_set_*` APIs.
- It writes PNG header/info, reads rows pass-by-pass, writes rows, then reads/writes end info.
- After cleanup, it reopens both files and compares them byte by byte.
- Return value is nonzero on setup/read/write errors; byte differences are reported but return `0` in this older test logic after printing diagnostics.

Notable implementation details:
- `SINGLE_ROWBUF_ALLOC` is enabled unless `PNG_DEBUG` is set, making buffer overruns easier to detect.
- Unknown chunks are read with `PNG_HANDLE_CHUNK_ALWAYS` and written with `PNG_HANDLE_CHUNK_IF_SAFE` where supported.
- In default single-file mode, the same file is tested three times, with status dots enabled on the second pass.
- Debug allocation tracking maintains a linked list of allocations and reports leaks after each test.
- The test warns that byte comparison can fail legitimately if zlib/libpng compression settings differ.
- The final typedef forces a compile error if an older `png.h` is found.

Important dependencies:
- Public libpng API from `png.h`.
- zlib version macro for diagnostics.
- C stdio unless `PNG_NO_STDIO` paths are built.
- Platform branches for Windows CE and RISC OS.

Research notes:
- This file is a useful executable integration test for the surrounding libpng sources.
- It uses file I/O only as a test harness, not as filesystem-layer logic.
- Audit attention should focus on old portability branches, test return semantics, and debug-only allocation tracker behavior.
