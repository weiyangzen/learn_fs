# sources/user-network-fs/mergerfs/vendored/fmt/os.h

## Purpose
`os.h` adds optional OS-facing functionality to fmt: C-string view wrappers, platform error helpers, RAII file descriptor and `FILE*` wrappers, pipes, page-size access, and a fast buffered output stream for files. It is an extension layer over `format.h`, not part of the core formatter parser.

## Important APIs, Types, and Functions
Public types include `basic_cstring_view`, `cstring_view`, `wcstring_view`, `buffered_file`, `file` when `FMT_USE_FCNTL` is enabled, `pipe`, `detail::buffer_size`, `detail::ostream_params`, and `ostream`. Public helpers include `system_category`, Windows-only `windows_error`/`vwindows_error`/`report_windows_error`, macOS-only `say`, `getpagesize`, `buffer_size`, and `output_file`. `file` exposes open flags (`RDONLY`, `WRONLY`, `RDWR`, `CREATE`, `APPEND`, `TRUNC`), `descriptor`, `close`, `size`, `read`, `write`, `dup`, `dup2`, `fdopen`, and Windows wide-path open support.

## Control Flow
Header setup detects whether `<fcntl.h>` and POSIX-like file APIs are usable, maps POSIX calls through `_`-prefixed Windows variants where necessary, and wraps system calls through `FMT_SYSTEM` for testability. `buffered_file` owns a `FILE*`, closes it in the destructor, supports move transfer, and formats by choosing buffered or regular `vprint` depending on argument locking traits. `file` owns an integer descriptor, closes in destructor, retries interrupted POSIX calls via `FMT_RETRY`, and can transfer ownership to `buffered_file` through `fdopen`. `ostream` owns a `file` and a `detail::buffer<char>`; `print` appends formatted bytes to the buffer, `flush` writes buffered bytes to the descriptor, and `close` flushes then closes.

## State and Persistence Behavior
The stateful objects in this header own OS resources. `buffered_file` persists an open `FILE*` until `close`, move assignment, or destruction. `file` persists a descriptor until `close`, move assignment, or destruction, using `-1` as the closed sentinel. `pipe` persists two descriptors. `ostream` persists buffered bytes in memory until flush, close, or destruction, then writes to the filesystem. These wrappers intentionally interact with durable external state: opening, truncating, appending, writing, duplicating, and closing files.

## Dependencies and Integration Points
The header depends on `format.h`, C runtime file APIs, POSIX file APIs when enabled, Windows CRT shims, `std::system_error`, optional `<xlocale.h>`, and optional Windows family detection. It integrates with fmt's `writer` abstraction by converting `ostream` to a `writer`, with fmt print APIs through `buffered_file::print` and `ostream::print`, and with mergerfs anywhere vendored fmt is used for file or error output.

## Risks
The primary risks are OS resource leaks or double-close behavior if ownership semantics are violated, platform gaps when `FMT_USE_FCNTL` is disabled, Windows invalid-parameter behavior on repeated close, short read/write handling, interrupted system calls outside Windows, and data loss if buffered `ostream` is not flushed before abnormal termination. `output_file` defaults to create/truncate, so accidental use can overwrite files. Because APIs throw `fmt::system_error` for failures, callers must not rely on silent failure.

## Test Signals
Useful tests include opening nonexistent files and checking system errors, RAII close on destruction, move-only transfer of descriptors and `FILE*`, read/write round trips, `dup`/`dup2`, pipe creation, `fdopen`, `output_file` flush and close behavior, custom buffer sizes, and platform-specific Windows wide-path and error-formatting paths. Build signals should cover both `FMT_USE_FCNTL=1` and a configuration where it is disabled.
