<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/fmt/xchar.h -->
# sources/user-network-fs/mergerfs/vendored/fmt/xchar.h

Purpose: This vendored fmt header adds optional wide-character and non-`char` formatting support on top of `format.h`, `color.h`, `ostream.h`, and `ranges.h`. It exports `wstring_view`, `wformat_context`, `wformat_args`, `wmemory_buffer`, `wformat_string`, wide `format`, `format_to`, `format_to_n`, `formatted_size`, `print`, `println`, `join`, and `to_wstring` APIs, plus generic overloads for exotic character types.

Important flow: compile-time format strings are represented by `basic_fstring<Char,T...>`, which invokes fmt's checker when consteval support is available. Runtime formatting builds a `basic_memory_buffer<Char>`, routes through `detail::vformat_to`, and parses format strings with a `format_handler`. Locale-aware overloads pass `locale_ref` down to `detail::write_loc`, which uses `std::numpunct<wchar_t>` when `FMT_USE_LOCALE` is enabled.

State and integration: the header owns no durable state; it allocates transient buffers and writes to caller-provided output iterators, `FILE*`, or `std::wostream`. It integrates with fmt's buffered context, named-argument support, range joins, text styling, and error handling via `FMT_THROW`.

Risks and test signals: wide output paths depend on C wide I/O semantics and locale availability. Exotic-character overload selection is SFINAE-heavy, so regressions usually appear as compile failures or ambiguous overloads. Useful tests compile wide and exotic string formatting, locale grouping, `format_to_n`, `join` for tuples/ranges, and FILE/wostream print error paths.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/fmt/xchar.h -->
