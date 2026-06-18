# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/libpng/pngtest.c

`pngtest.c` is the bundled libpng self-test program. It reads a PNG, writes it back out through libpng, compares input and output bytes, and reports pass/fail. It also exercises optional callback, custom I/O, custom memory, unknown chunk, interlace, text, metadata, and timing paths depending on compile-time feature macros.

Program flow:
- `main` prints libpng/zlib version information, validates header/library version consistency, parses `-m`, `-mv`, `-vm`, `-v`, input, and output arguments, then calls `test_one_file`.
- In single-file mode it runs the same input up to three times with different progress verbosity behavior.
- In multi-file mode it reuses `pngout.png` or the configured output as a temporary comparison output.
- `test_one_file` opens input/output, creates read/write structs and info structs, sets error handling and setjmp recovery, initializes I/O, reads PNG info, copies metadata from read info to write info, streams all rows from reader to writer, reads/writes end info, destroys structs, closes files, then byte-compares original and output.

Metadata copying:
- Copies `IHDR`, cHRM, gAMA, iCCP, sRGB, PLTE, bKGD, hIST, oFFs, pCAL, pHYs, sBIT, sCAL, text, tIME, tRNS, and unknown chunks when the matching feature macros are enabled.
- For unknown chunks, preserves recorded chunk locations by calling `png_set_unknown_chunk_location` after `png_set_unknown_chunks`.
- Calls `png_set_keep_unknown_chunks` on read/write structs so test output can retain configured unknown chunks.

Callbacks and optional test hooks:
- `read_row_callback` and `write_row_callback` print progress characters for row callbacks.
- `count_filters` is a read user transform callback that counts filter bytes used by decoded rows.
- `count_zero_samples` is a write user transform callback that counts zero-valued samples/pixels.
- Under `PNG_NO_STDIO`, local `pngtest_read_data`, `pngtest_write_data`, and `pngtest_flush` validate custom I/O callbacks.
- Under `PNG_USER_MEM_SUPPORTED && PNG_DEBUG`, `png_debug_malloc` and `png_debug_free` track allocations, detect leaks, poison memory on allocate/free, and print allocation diagnostics in verbose mode.
- Optional `PNGTEST_TIMING` records decode, encode, and miscellaneous CPU time.

Important dependencies and state:
- Includes `png.h` plus standard C headers or Windows CE APIs depending on platform.
- Uses zlib `ZLIB_VERSION`, libpng public APIs, optional feature macros, and setjmp-based libpng error handling.
- Static globals track verbosity, progress dot state, tIME display state, zero-sample/filter counters, and debug allocation state.

Edge cases and risks:
- The byte-for-byte comparison can legitimately fail when compression level, filter heuristics, zlib version, maximum IDAT size, or unknown chunk handling differ; the program documents this and prints diagnostic hints.
- The program is a regression harness, not a comprehensive transform tester. It mostly validates read/write preservation and basic row streaming.
- Much of the file is conditional portability code for old platforms, far pointers, Windows CE, no-stdio builds, custom memory, and optional callbacks.
- Error cleanup paths must keep read/write structs, row buffers, and file handles paired with the correct libpng owner because setjmp can exit from deep library calls.
