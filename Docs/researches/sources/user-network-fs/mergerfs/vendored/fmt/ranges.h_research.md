# sources/user-network-fs/mergerfs/vendored/fmt/ranges.h

## Purpose
`ranges.h` adds formatting support for ranges, maps, sets, tuple-like types, container adaptors, and `fmt::join`. It detects begin/end and tuple protocols, chooses an appropriate presentation category, and composes element formatters with delimiters.

## Important APIs, Types, and Functions
Public APIs include `range_format`, `is_tuple_like`, `is_tuple_formattable`, `is_range`, `range_formatter`, `range_format_kind`, tuple/range/map/string formatter specializations, `join_view`, `tuple_join_view`, and `fmt::join` overloads for iterator pairs, ranges, tuples, and initializer lists. Internal helpers include `range_begin`, `range_end`, `is_map`, `is_set`, begin/end detection traits, tuple detection and index-sequence helpers, `for_each`, `for_each2`, `range_reference_type`, `uncvref_type`, `parse_empty_specs`, `format_tuple_element`, `is_container_adaptor_like`, and `detail::all`.

## Control Flow
Type selection is compile-time. Tuple-like non-range values format with parentheses by default and parse optional `n` to remove brackets and separators. Ranges are classified as disabled, map, set, sequence, string, or debug string. `range_formatter` parses range-level controls such as `n`, `s`, `?s`, and optional nested element specs after `:`, then iterates begin/end at runtime and formats each element with the underlying element formatter. Sets use braces, sequences use brackets, maps use braces and format key/value tuple elements separated by `": "`. `join` returns view objects whose formatters output elements separated by the requested separator without outer brackets.

## State and Persistence Behavior
Formatter objects store delimiter strings, bracket strings, debug-string flags, and underlying element formatter instances. Runtime formatting only reads the supplied range or tuple and writes to the format context. `join_view` stores iterators/sentinel and a separator view, so it depends on the referenced range and separator data remaining alive through formatting. No persistent external state is created.

## Dependencies and Integration Points
The header depends on `format.h`, tuple utilities, iterator utilities, initializer lists, type traits, and ADL `begin`/`end`. It integrates with fmt's general `formatter<T, Char>` selection, with standard containers through their member begin/end and map/set typedefs, with tuple-like standard and user types through `std::tuple_size`/`std::tuple_element`/`get`, and with container adaptors by accessing the protected `c` member through a derived helper.

## Risks
Compile-time detection can surprise user types that expose `key_type`, `mapped_type`, tuple protocol, or begin/end-like APIs unintentionally. `join` can dangle if called with a temporary range whose iterators do not survive until formatting. Container adaptor formatting relies on the conventional protected member `c`, which is standard for adaptors but still implementation-sensitive. Formatting very large or single-pass ranges consumes the range during formatting. Debug string paths copy character ranges into a buffer before escaping.

## Test Signals
Tests should cover vectors/lists/arrays, maps, sets, tuples, pairs, nested ranges, custom ADL ranges, non-const-only and const-only ranges, character ranges with `s` and `?s`, no-delimiter `n`, nested element specs through `:`, `fmt::join` over iterator pairs/ranges/tuples/initializer lists, queue/stack/priority_queue adaptor output, and dangling-prone usage rejected by review or covered by lifetime tests where possible.
