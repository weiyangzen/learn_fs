# sources/storage-engines/rocksdb/file/line_file_reader.h

## Purpose

`line_file_reader.h` declares `LineFileReader`, a non-copyable wrapper around `SequentialFileReader` for newline-delimited text reads using RocksDB filesystem, IO status, and rate-limiting conventions.

## Important APIs, Types, and Functions

- Internal fields: `std::array<char, 8192> buf_`, `SequentialFileReader sfr_`, `IOStatus io_status_`, buffer begin/end pointers, `line_number_`, and `at_eof_`.
- Variadic constructor forwards arguments to `SequentialFileReader`.
- Static `Create(...)` opens and wraps a file via `FileSystem`.
- `ReadLine(std::string*, Env::IOPriority)` returns the next line without delimiter.
- `GetLineNumber()` reports the most recently returned line count.
- `GetStatus()` exposes the permanent read status.

## Control Flow and State

The header defines the reader's state model: one buffered sequential scan with monotonically increasing line number and no recovery after IO error. It prevents copying so buffer pointers and file-reader ownership cannot be duplicated accidentally.

## Dependencies and Integration Points

The header depends on `file/sequence_file_reader.h`, which supplies the actual sequential file wrapper and IO/rate-limiter behavior. Consumers get a simple line API without depending directly on `FSSequentialFile`.

## Risks and Edge Cases

- `GetLineNumber()` is unspecified after IO-error false returns, so callers should check `GetStatus()`.
- The `ReadLine` contract requires callers to distinguish EOF from failure.
- The forwarding constructor makes construction flexible but also means invalid `SequentialFileReader` argument combinations are diagnosed by that lower layer.

## Test Signals

Direct tests are not present in this subset. Coverage should focus on EOF semantics, delimiter stripping, line counting, rate-limiter priority forwarding, and permanent error handling.
