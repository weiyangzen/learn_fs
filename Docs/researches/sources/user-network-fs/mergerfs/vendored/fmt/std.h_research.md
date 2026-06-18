# sources/user-network-fs/mergerfs/vendored/fmt/std.h

## Purpose
`std.h` provides fmt formatter specializations and helpers for many standard-library types. It extends core formatting to filesystem paths, bitsets, thread ids, optional, expected, source locations, variants, error codes, type info, exceptions, bit-reference proxies, atomics, complex numbers, smart pointers, and reference wrappers.

## Important APIs, Types, and Functions
Public helpers include `fmt::ptr` overloads for `std::unique_ptr` and `std::shared_ptr`, and the filesystem compatibility `fmt::path` wrapper when filesystem support is available. Formatter specializations cover `std::filesystem::path`, `std::bitset<N>`, `std::thread::id`, `std::optional<T>`, `std::expected<T,E>`, `std::source_location`, `std::monostate`, `std::variant`, `std::error_code`, `std::type_info`, `std::exception` subclasses, bit-reference-like proxy types, `std::atomic<T>`, `std::atomic_flag`, `std::complex<T>`, and `std::reference_wrapper<T>`. Internal helpers include path conversion/escaping, variant/expected alternative escaping, demangling and ABI-name normalization, bit-reference detection, and `format_as` guards for reference wrappers.

## Control Flow
Feature macros gate optional standard-library support based on headers and `__cpp_lib_*` values. Filesystem paths parse alignment, width, debug `?`, and generic `g` options, then either write native/generic path strings or escaped debug path strings with UTF-16 to UTF-8 conversion where needed. Optional and expected format as `optional(...)`, `none`, `expected(...)`, or `unexpected(...)`. Variants visit the active alternative and format it with debug escaping where applicable, catching `bad_variant_access`. Error codes parse width/debug/string options and output either `category:value` or `message`. Complex numbers parse numeric specs, format `(real+imagi)` when the real part is nonzero and `imagi` otherwise, with outer width applied after composing into a temporary buffer.

## State and Persistence Behavior
Formatter instances store parsed specs and small flags such as debug mode, path type, and exception typename mode. Formatting is read-only with respect to input objects except atomics, which perform `load()`, and `atomic_flag`, which performs `test()` when available. Temporary memory buffers are used for escaped paths, error-code strings, complex numbers with width, and demangled names. No external persistent state is modified.

## Dependencies and Integration Points
The header depends on `format.h` and `ostream.h`, plus many conditional standard headers: atomic, bitset, complex, exception, functional, memory, thread, typeinfo, filesystem, variant, optional, source_location, expected, and version. ABI demangling uses `<cxxabi.h>` when available and RTTI when enabled. It integrates with `ranges.h` indirectly by avoiding `format_as` traps and using nested/string formatters, and with ostream formatting for `std::thread::id`.

## Risks
Behavior varies significantly with compiler, standard-library, RTTI, and feature-test macros. Filesystem formatting has platform encoding risk, especially Windows wide native paths and invalid UTF-16 replacement. Demangled type names are ABI- and standard-library-specific despite normalization. Exception formatting with `t` only includes type names when RTTI is enabled. Atomic formatting observes a momentary value only. Variant and expected formatting require all alternatives to be formattable, and alternative string/char values are debug-escaped. `std::complex` uses numeric specs for components, so invalid specs surface through underlying numeric formatting.

## Test Signals
Tests should cover each feature macro path available in the build: filesystem native/generic/debug output, bitset padding, thread id ostream formatting, optional engaged/empty, expected value/error, source location layout, variant alternatives and valueless handling, error_code default/string/debug forms, exception `what()` and optional type name, bit-reference proxies such as `vector<bool>::reference`, atomic and atomic_flag formatting, complex real/imaginary/non-finite values, smart-pointer `ptr`, and reference_wrapper forwarding.
