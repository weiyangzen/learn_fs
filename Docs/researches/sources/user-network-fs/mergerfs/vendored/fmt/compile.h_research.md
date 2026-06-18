# sources/user-network-fs/mergerfs/vendored/fmt/compile.h

Read signal: read `sources/user-network-fs/mergerfs/vendored/fmt/compile.h` completely for this pass (588 lines). Final split target: `Docs/researches/sources/user-network-fs/mergerfs/vendored/fmt/compile.h_research.md`.

## Purpose

`compile.h` implements fmt's experimental compile-time format-string compilation layer. It converts `FMT_COMPILE("...")` or, when enabled, the `"_cf"` literal into a small constexpr representation that can format directly without reparsing the format string at runtime. It sits above `format.h`: the generated representation still calls core fmt writing and `formatter<T, Char>` machinery for actual value formatting.

The file is intentionally feature-gated. The fast compile path is enabled only when the compiler supports `constexpr if` and return type deduction. C++20 non-type template parameters add the optional `"_cf"` literal. Otherwise `FMT_COMPILE` falls back to `FMT_STRING`, preserving compile-time format checking but not necessarily the direct compiled representation.

## Important APIs, Types, and Functions

- `fmt::compiled_string` is a marker base type. `is_compiled_string<S>` identifies FMT string wrapper types produced by `FMT_COMPILE`.
- `FMT_COMPILE(s)` wraps a string literal through `FMT_STRING_IMPL(s, fmt::compiled_string)` when the constexpr compile path is available; otherwise it maps to `FMT_STRING(s)`.
- `fmt::literals::operator""_cf` converts a `detail::fixed_string` to the same compiled-string wrapper when `FMT_USE_NONTYPE_TEMPLATE_ARGS` is true.
- `detail::type_list`, `detail::get<N>`, and `detail::get_type<N, type_list<...>>` are compile-time utilities for resolving a replacement field's argument type from a parameter pack.
- `detail::text<Char>`, `detail::code_unit<Char>`, `detail::field<Char, V, N>`, `detail::spec_field<Char, V, N>`, `detail::runtime_named_field<Char>`, and `detail::concat<L, R>` form the compiled format AST. Each type has a `format(out, args...)` method.
- `detail::compile_format_string<Args, POS, ID>(fmt)` recursively parses literals, escaped braces, positional fields, named fields, and specifier-bearing fields into that AST.
- `detail::parse_specs<T>` instantiates `formatter<T, Char>`, runs its `parse` method under `compile_parse_context`, and stores the parsed formatter inside `spec_field`.
- Public overloads of `fmt::format`, `fmt::format_to`, `fmt::format_to_n`, `fmt::formatted_size`, and `fmt::print` accept compiled-string inputs and dispatch either to the compiled AST or to normal runtime formatting when the compiler cannot statically resolve a field.
- `fmt::static_format_result<N>` and `FMT_STATIC_FORMAT` produce a compile-time, null-terminated result whose size is computed with `formatted_size(FMT_COMPILE(...), ...)`.

## Control Flow

`FMT_COMPILE` creates a type that carries the literal and inherits `compiled_string`. Public `format`/`format_to` overloads then call `detail::compile<T...>(S())`, which builds `basic_string_view` over the literal and invokes `compile_format_string<type_list<T...>, 0, 0>`.

The recursive parser walks the string at compile time. Literal spans become `text`; single literal code units can become `code_unit`; escaped `{{` and `}}` become text; replacement fields resolve either automatic indexes, explicit numeric indexes, compile-time named indexes, or runtime named fields. A field without format specs becomes `field`; a field with specs becomes `spec_field` after parsing the formatter. Each parsed head is joined with the remaining tail through `concat`.

Argument-index state is tracked through the integer template parameter `ID`; `manual_indexing_id == -1` marks explicit indexing. `static_assert`s reject switching from automatic to manual indexing or vice versa. Missing braces and unsupported compile-time forms are rejected with `format_error` or `static_assert`, while named fields with unknown type information and format specs return `unknown_format` so public overloads can fall back to normal runtime `fmt::format`.

The formatted output path is simple: `concat::format` calls `lhs.format` then `rhs.format`; `field::format` extracts the Nth argument with `get_arg_checked`, unwraps named arguments, and writes either string-view data directly or routes the value through `write`; `spec_field::format` creates a `basic_format_context` from `make_format_args` and calls the stored `formatter`.

## State and Persistence Behavior

The file has no external persistence and no global mutable state. The compiled representation is embodied in constexpr object types and in local formatter objects stored inside `spec_field`. Output state is carried by the caller-provided output iterator or by temporary buffers used by `format`, `format_to_n`, `formatted_size`, and `print`.

The only stateful decisions are compile-time parser state: current position, next automatic argument id, and the manually indexed sentinel. Runtime named-field lookup is transient and folds across the function arguments.

## Dependencies and Integration Points

`compile.h` includes `format.h` and uses fmt internals such as `basic_string_view`, `formatter`, `compile_parse_context`, `arg_ref`, `arg_id_kind`, `parse_arg_id`, `basic_format_context`, `make_format_args`, `write`, `copy`, `memory_buffer`, `counting_buffer`, `appender`, `fixed_buffer_traits`, and `iterator_buffer`. It also uses `<iterator>` for `std::back_inserter` unless building as a module.

The public API integrates with regular fmt overload sets via SFINAE on `is_compiled_string` and `is_compiled_format`, so callers can pass compiled wrappers to standard `fmt::format`-style functions. In mergerfs this vendored fmt layer is a dependency implementation detail rather than mergerfs-specific logic.

## Risks and Edge Cases

- This is experimental and compiler-feature dependent; behavior changes across C++ standard modes and vendor support are expected.
- Compile-time named arguments with specs require type information. Unknown named fields with `:` fall back to runtime formatting, while unknown named fields without specs use `runtime_named_field`.
- `get_type<N>` and `get<N>` produce compile-time failures if a field index exceeds the provided argument pack.
- The direct `"{}"` char-format fast path calls `fmt::to_string` on the first argument, with special unwrapping for named args; tests should cover that shortcut separately from the general AST path.
- `format_to_n` fixes the buffer character type to `char` in this file's overload, which is consistent with this vendored fmt version but is worth checking if wide-character compiled strings are used.
- Because `spec_field` stores a parsed `formatter<V, Char>`, formatter parse behavior must be constexpr-compatible for full compile-time compilation.

## Test Signals

Useful signals include compile-only tests for `FMT_COMPILE`, automatic and manual index rejection, escaped braces, named arguments, unknown named fallback, fields with custom format specs, `format_to`, `format_to_n`, `formatted_size`, `print`, and `FMT_STATIC_FORMAT`. Cross-compiler builds should exercise C++14/17/20 gates, `FMT_USE_NONTYPE_TEMPLATE_ARGS`, and compilers without `constexpr if` to ensure fallback to `FMT_STRING` still works.
