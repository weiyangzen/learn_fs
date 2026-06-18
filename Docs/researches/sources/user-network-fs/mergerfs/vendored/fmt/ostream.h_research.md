# sources/user-network-fs/mergerfs/vendored/fmt/ostream.h

## Purpose
`ostream.h` provides integration between fmt and `std::ostream`. It allows values with an `operator<<` to be formatted through fmt, and it adds `fmt::print`/`fmt::println` overloads that write formatted data to a `std::ostream`.

## Important APIs, Types, and Functions
Important APIs include `basic_ostream_formatter`, the `ostream_formatter` alias, `detail::streamed_view`, `fmt::streamed`, `fmt::vprint(std::ostream&, string_view, format_args)`, `fmt::print(std::ostream&, format_string<T...>, T&&...)`, and `fmt::println(std::ostream&, format_string<T...>, T&&...)`. Internal helpers include `detail::write_buffer`, `detail::formatbuf` from `chrono.h`, and platform-specific file-buffer access helpers used to detect Windows console streams.

## Control Flow
`basic_ostream_formatter::format` creates a fmt memory buffer, wraps it in `detail::formatbuf`, constructs a temporary `std::basic_ostream`, imbues the classic locale, streams the value with `operator<<`, then formats the resulting buffer as a string view using any outer fmt string specs. `streamed(value)` creates a lightweight view that selects this formatter explicitly. `print(os, ...)` formats into a memory buffer, then writes to the stream with `write_buffer`; in UTF-8 Windows console cases, `vprint` tries to retrieve the underlying `FILE*`, flushes the stream, and delegates to `detail::write_console`.

## State and Persistence Behavior
This header stores no global state. Formatting via `basic_ostream_formatter` uses temporary buffers and streams. `print` and `println` mutate the target `std::ostream` by writing bytes and may flush it on Windows console paths. Stream exception settings are applied to the temporary stream used for `operator<<`, so insertion failures become stream exceptions there. No filesystem state is created unless the supplied stream is backed by a file.

## Dependencies and Integration Points
The header depends on `chrono.h` for `formatbuf`, `format.h` transitively, `<fstream>`, and platform-specific Windows/GLIBCXX stream buffer details when available. It integrates fmt with legacy types that only implement `operator<<`, with `std::thread::id` formatting from `std.h`, and with user code that wants fmt syntax but an existing C++ stream sink.

## Risks
The biggest risk is semantic mismatch between fmt formatting and stream insertion: streamed values use the classic locale and only then receive outer string formatting. Windows console optimization depends on RTTI and implementation-specific `std::filebuf` internals, so it may be inactive or fragile across standard libraries. `println` formats the message to a string and then prints `"{}\n"`, causing an extra allocation relative to direct buffer append. Stream insertion can throw or set failure states depending on the value's `operator<<`.

## Test Signals
Tests should verify `fmt::streamed` for custom `operator<<` types, width/alignment applied to the streamed result, direct `print` and `println` to `std::ostringstream`, large buffer writes beyond `std::streamsize` chunks, classic-locale behavior, and Windows console UTF-8 handling where available. Negative tests should cover stream insertion failures.
