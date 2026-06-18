# sources/user-network-fs/mergerfs/vendored/fmt/format-inl.h

Read signal: read `sources/user-network-fs/mergerfs/vendored/fmt/format-inl.h` completely for this pass (1948 lines). Final split target: `Docs/researches/sources/user-network-fs/mergerfs/vendored/fmt/format-inl.h_research.md`.

## Purpose

`format-inl.h` contains non-header-only implementation details for the vendored fmt formatting library. It supplies out-of-line or conditionally inline definitions for assertion failure, locale-aware formatting helpers, system-error formatting, Dragonbox floating-point decimal conversion, bigint formatting support, UTF-8 to UTF-16 conversion, runtime `vformat`, FILE/console printing, and Unicode printable-code-point lookup.

This file is implementation infrastructure for `format.h`; it is not mergerfs-specific. Its correctness directly affects all formatting, printing, diagnostics, and floating-point rendering performed through the vendored fmt copy.

## Important APIs, Types, and Functions

- `assert_fail(file, line, message)` reports failed fmt assertions to `stderr` and aborts unless `FMT_CUSTOM_ASSERT_FAIL` overrides it.
- `locale_ref::get<Locale>()`, fallback `detail::locale`, `detail::numpunct`, `thousands_sep_impl`, `decimal_point_impl`, and `write_loc` provide locale support when `FMT_USE_LOCALE` is enabled and predictable comma/period defaults otherwise.
- `format_error_code`, `format_system_error`, `report_system_error`, `do_report_error`, `vsystem_error`, and `report_error` are the error-reporting and exception construction utilities.
- `detail::dragonbox` contains the fast binary floating-point to shortest decimal conversion implementation. Key pieces are `cache_accessor<float>`, `cache_accessor<double>`, `get_cached_power`, `remove_trailing_zeros`, `shorter_interval_case`, and `to_decimal<T>`.
- `formatter<detail::bigint>` prints fmt's internal bigint in hexadecimal bigit order and appends a power marker when the bigint exponent is positive.
- `detail::utf8_to_utf16::utf8_to_utf16` converts UTF-8 to a null-terminated UTF-16/wchar buffer for Windows console output.
- `vformat`, `detail::vformat_to`, `vprint_buffered`, `vprint`, `vprintln`, and `detail::print` are runtime formatting and output entry points.
- `file_base`, `glibc_file`, `apple_file`, `fallback_file`, `file_print_buffer`, `get_file`, `has_flockfile`, and wrapper functions around `flockfile`/`funlockfile`/`getc_unlocked` implement optimized FILE-buffer integration when libc internals are available.
- `write_console` and `vprint_mojibake` handle Windows console and legacy encoding cases.
- `detail::is_printable(uint32_t)` uses generated tables to decide whether Unicode code points should be treated as printable.

## Control Flow

The top of the file sets platform includes and `FMT_FUNC`, then defines assertion and locale utilities. Error formatting paths first try high-level standard library messages (`std::system_error`) and fall back to bounded inline-buffer messages such as `"error N"` if allocation or formatting fails. `do_report_error` writes to `stderr` without throwing.

Floating-point formatting flows through `detail::dragonbox::to_decimal<T>`. It bit-casts the float/double, extracts exponent and significand fields, handles zero/subnormal/normal cases, computes a cached power of ten, and derives the shortest decimal significand/exponent pair. Normal powers with zero significand can use `shorter_interval_case`; other values execute the regular path: compute scaled interval endpoints, try the larger decimal divisor, compare endpoint inclusion and parity, remove trailing zeros, and fall back to the small-divisor path when necessary. `cache_accessor<double>` either uses the full cached-power table or reconstructs cache entries from a compressed table plus powers of five, depending on `FMT_USE_FULL_CACHE_DRAGONBOX`.

Runtime string formatting enters `vformat`, allocates a `memory_buffer`, calls `detail::vformat_to`, then converts the buffer to `std::string`. `detail::vformat_to` optimizes the exact `"{}"` case by visiting argument zero directly; otherwise it calls `parse_format_string` with a `format_handler` constructed from parse context, output appender, arguments, and locale.

Printing selects between buffered and direct paths. `vprint` checks whether the detected `FILE` wrapper is buffered and whether `flockfile` support exists. If not, it formats into a `memory_buffer` and writes with `fwrite_all`. If yes, `file_print_buffer` locks the FILE, points fmt's buffer at the libc write buffer, advances it as data is produced, and unlocks/flushed as needed. On Windows non-`FMT_USE_WRITE_CONSOLE` builds, `detail::print` detects TTY output, converts UTF-8 to UTF-16, and calls `WriteConsoleW`; otherwise it writes bytes.

Unicode printability is a table lookup: `is_printable(uint32_t)` selects generated singleton and range tables for BMP and supplementary planes, then rejects a handful of explicit high-plane ranges and bounds at `0x110000`.

## State and Persistence Behavior

The file has no repository or disk persistence. It does maintain process-local static constants: Dragonbox cached power tables, small power tables, and generated Unicode printability tables. Locale state is read through `locale_ref`; fallback locale behavior is stateless.

I/O state is transient but important: `file_print_buffer` temporarily locks a `FILE*`, writes directly into its internal buffer when supported, advances libc write pointers, and may flush line-buffered streams. `fwrite_all` and `file_base::get/unget` interact with `errno` and C stream error state. Windows console output temporarily materializes a UTF-16 buffer.

## Dependencies and Integration Points

`format-inl.h` includes `format.h` and standard headers for algorithms, errno, limits, math, exceptions, and optional locale support. It depends heavily on fmt internals declared elsewhere: buffers, appenders, parse contexts, `format_handler`, `loc_writer`, `format_facet`, integer traits, `basic_fp`, `float_info`, `uint128_fallback`, `bigint`, UTF code-point iteration, and value visitors.

Platform integration points include glibc `FILE` internals (`_IO_read_ptr`, `_IO_write_ptr`, `_flags`), Apple libc internals (`_p`, `_r`, `_w`, `_bf`), MSVC `_lock_file`/`_unlock_file` and `_fgetc_nolock`, POSIX-style `flockfile`, Windows `_isatty`, `_fileno`, `_get_osfhandle`, and `WriteConsoleW`. Build macros such as `FMT_USE_LOCALE`, `FMT_USE_FULL_CACHE_DRAGONBOX`, `FMT_USE_FALLBACK_FILE`, `FMT_USE_WRITE_CONSOLE`, `FMT_MODULE`, `_WIN32`, and `FMT_CUSTOM_ASSERT_FAIL` materially change compiled behavior.

## Risks and Edge Cases

- Dragonbox arithmetic is precision-critical. Incorrect cached powers, shifts, endpoint inclusion, parity checks, or trailing-zero removal will produce wrong float/double text, often only for narrow boundary values.
- The compressed double cache path is more complex than the full table path and should be tested separately.
- FILE-buffer optimization relies on libc private struct layouts. The SFINAE probes and `FMT_USE_FALLBACK_FILE` reduce portability risk, but libc changes can break assumptions.
- `file_print_buffer` writes directly to stream buffers while holding locks; exception safety and flush-on-newline behavior are important for partially formatted output.
- `format_error_code` intentionally avoids dynamic allocation by fitting into `inline_buffer_size`; long messages can be dropped before appending `"error N"`.
- Windows console output assumes input text is UTF-8 and throws on invalid UTF-8 during conversion; byte-oriented fallback writes legacy encoded output.
- Generated Unicode printable tables are opaque and must stay in sync with the fmt version's Unicode policy.
- `assert_fail` aborts the process after writing to `stderr`, which is appropriate for internal assertions but severe if an assertion is reachable from malformed user input.

## Test Signals

High-value tests include fmt's upstream floating-point formatting corpus, boundary floats/doubles around powers of ten, subnormals, signed zero, infinities/NaN through the surrounding formatter path, locale grouping/decimal behavior, `std::system_error` fallback behavior under allocation failure if testable, `vformat("{}")` fast path, ordinary parsed format strings, `vprint` to buffered and unbuffered files, Windows console UTF-8 output, invalid UTF-8 handling, line-buffered flush behavior, and Unicode escaping/printability cases around table boundaries such as BMP singletons and the explicit high-plane ranges.
