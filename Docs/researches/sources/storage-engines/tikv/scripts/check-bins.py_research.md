# sources/storage-engines/tikv/scripts/check-bins.py

## Purpose
CI helper that inspects built binaries for allocator, CPU-instruction, system-library, and OpenSSL linkage policy. It checks test binaries from Cargo JSON and release binaries passed on the command line.

## Important APIs and Control Flow
`ensure_link` uses `ldd` on Linux to require or forbid dynamic libraries. `check_jemalloc` scans `readelf -s` for jemalloc symbols. `check_sse` uses `nm` and `objdump` to confirm `crc32c_3way` contains the SSE4.2 `crc32` opcode. `check_openssl` checks static or dynamic OpenSSL expectations and rejects text-section OpenSSL symbols when dynamic linking is expected. `check_tests` consumes Cargo JSON from stdin and skips a whitelist; `check_release` validates explicitly supplied binaries. `main` parses optional `--features` and dispatches to `--check-tests` or `--check-release`.

## State, Dependencies, Integration
The script is read-only apart from stdout/stderr and exit status. It depends on Python, Linux tools (`ldd`, `readelf`, `nm`, `objdump`, `uname`), TiKV feature names, and Cargo JSON output. `scripts/test-all` pipes a no-run cargo test build into it.

## Risks and Test Signals
Shell command construction through `os.popen` is path-sensitive. Non-Linux systems skip linkage checks. Symbol and opcode checks are coupled to allocator, RocksDB CRC, and OpenSSL implementations. Passing output and exit 0 are the main signals; negative fixtures should cover missing jemalloc, missing SSE4.2, and OpenSSL linkage mismatches.
