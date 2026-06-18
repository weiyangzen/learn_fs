# sources/test-tools/fio/t/verify-state.c

Purpose: diagnostic utility that decodes fio verify-state files into plain text. It validates the file header size and CRC before printing per-thread verify state and inflight write numbers.

Important APIs and types: it consumes `struct verify_state_hdr`, `struct thread_io_list`, and inflight entries from `verify-state.h`. `show_s()` prints one thread record. `show()` performs little-endian conversion for each variable-length thread record. `show_verify_state()` validates header metadata and CRC using `fio_crc32c()`. `show_file()` handles file I/O.

Control flow: `main()` initializes debugging, requires at least one state-file path, and processes files in order until one fails. `show_file()` opens, stats, allocates a buffer, reads the entire file, and calls `show_verify_state()`. The decoder checks header size, verifies CRC over the payload, rejects unsupported versions, then iterates through thread records using `__thread_io_list_sz(depth)`.

State and persistence: read-only over input files. It allocates a whole-file buffer per state file and frees it after printing. No output files are written.

Dependencies and integration points: depends on fio internals for logging, OS endian helpers, verify-state layout, CRC32C, and debug initialization. It is useful alongside fio verify-state-save features and tests, but it is not shown as a direct umbrella test entry in this subset.

Risks and test signals: malformed files with inconsistent sizes stop decoding cleanly, but the loop in `show()` assumes the remaining payload is exactly a sequence of valid variable-length records. Success signals are printed version/size/CRC plus thread details; failures produce log errors for open/stat/read, short read, size mismatch, CRC mismatch, or unsupported version.
