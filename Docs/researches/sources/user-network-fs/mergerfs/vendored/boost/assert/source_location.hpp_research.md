<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/assert/source_location.hpp -->
# sources/user-network-fs/mergerfs/vendored/boost/assert/source_location.hpp

## Purpose
This header supplies `boost::source_location`, a small value type for file/function/line/column data, plus `BOOST_CURRENT_LOCATION` for capturing the current call site across C++ standards and compilers.

## Important APIs, Types, And Control Flow
`boost::source_location` stores `char const* file_`, `char const* function_`, and `boost::uint_least32_t` line/column fields. It has a default unknown-location constructor, a direct constructor, and an optional constructor from `std::source_location`. Accessors return file name, function name, line, and column. `to_string()` formats unknown locations specially, otherwise appends `:line`, optional `:column`, and optional function text. Equality compares string contents plus numeric fields, and `operator<<` is provided when iostreams are available.

## State And Persistence
Instances are plain values referencing string literals or caller-provided character storage. The header stores no global state and performs no persistence beyond temporary string formatting.

## Dependencies And Integration Points
It includes Boost.Config, Boost.Cstdint, `<string>`, `<cstdio>`, `<cstring>`, optional `<iosfwd>`, and optional `<source_location>`. `BOOST_CURRENT_LOCATION` selects among disabled mode, MSVC builtins, standard `std::source_location`, Clang/GCC builtins, `__PRETTY_FUNCTION__`, or a `__FILE__/__LINE__` fallback. It feeds Boost assertion diagnostics and any mergerfs code that wants source locations without hard requiring C++20.

## Risks And Test Signals
Risks include pointer lifetime when direct constructors receive non-static strings, compiler-specific builtin availability, NVCC constexpr limitations, and string comparison cost. Test signals include compile tests on C++03 through C++20, MSVC `/ZI`, GCC/Clang builtins, `BOOST_DISABLE_CURRENT_LOCATION`, iostream-disabled builds, and formatting equality checks.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/boost/assert/source_location.hpp -->
