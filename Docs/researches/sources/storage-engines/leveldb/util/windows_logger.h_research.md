# sources/storage-engines/leveldb/util/windows_logger.h

## Purpose
Implements `WindowsLogger`, the Windows counterpart to `PosixLogger`. It writes timestamped, thread-tagged log messages to an owned `FILE*`.

## Important APIs, Types, And Functions
The constructor asserts a non-null `std::FILE*` and takes ownership. The destructor closes it. `Logv` uses `GetLocalTime` to fill a `SYSTEMTIME`, formats the current C++ thread id, writes a fixed timestamp/thread prefix plus the caller message, appends a newline if needed, writes with `fwrite`, and flushes.

## Control Flow
Like the POSIX logger, it first formats into a 512-byte stack buffer and retries once with a dynamically allocated buffer when the formatted message does not fit. `va_copy` protects the input `va_list` across attempts.

## State And Persistence Behavior
Every log call writes and flushes to the owned file handle. There is no persistent state besides the file pointer, and no explicit lock around formatting or writing.

## Dependencies And Integration Points
It depends on Windows time APIs being available through the Windows environment compilation context, plus C stdio, C++ thread streams, and `leveldb/env.h`. Windows environment code instantiates it as the concrete `Logger`.

## Risks And Edge Cases
The comment says "PosixLogger instance" in the constructor documentation, a copy/paste documentation bug. Timestamp resolution is milliseconds multiplied to microseconds, unlike POSIX `gettimeofday`. Long-message handling relies on conforming `vsnprintf` sizing.

## Test Signals
There is no direct unit test in this subset. Signals are successful Windows builds, correctly formatted log files, newline insertion, and no file-handle leaks on logger destruction.
