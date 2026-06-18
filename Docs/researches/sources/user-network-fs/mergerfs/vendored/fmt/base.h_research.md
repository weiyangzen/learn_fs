# sources/user-network-fs/mergerfs/vendored/fmt/base.h

## Purpose

This fmt header is the base API for char/UTF-8 formatting. It defines version and portability macros, core type traits, string views, parse contexts, format-spec parsing, type-erased argument storage, output buffers, compile-time format string checking, default native formatter scaffolding, and public `format_to`, `formatted_size`, `print`, and `println` entry points.

## Important APIs, types, and functions

Public surface includes `FMT_VERSION 120100`, `fmt::basic_string_view`, `fmt::string_view`, `fmt::parse_context`, `fmt::locale_ref`, `fmt::formatter`, `fmt::format_context`, `fmt::format_args`, `fmt::basic_format_arg`, `fmt::basic_format_args`, `fmt::basic_appender`, `fmt::format_string`, `fmt::runtime`, `fmt::make_format_args`, `fmt::arg`, `fmt::vformat_to`, `fmt::format_to`, `fmt::format_to_n`, `fmt::formatted_size`, `fmt::print`, and `fmt::println`.

Important internal types include `basic_specs`, `format_specs`, `dynamic_format_specs`, `type_mapper`, `value<Context>`, `format_arg_store`, `named_arg_store`, `native_formatter`, `buffer`, `iterator_buffer`, `container_buffer`, `counting_buffer`, `compile_parse_context`, and `format_string_checker`.

## Control Flow

The top of the file configures compiler, standard library, constexpr, consteval, exception, visibility, inlining, namespace, Unicode, and ABI-related macros. Runtime formatting flow starts with a public API building a `vargs`/`format_arg_store`, converting it to `format_args`, and dispatching to `detail::vformat_to` or print functions declared here and defined in `format.h`/the fmt library.

Format-string parsing is a scanner over text and replacement fields. `parse_format_string` walks literal text, handles escaped braces, and delegates replacement fields to `parse_replacement_field`. Argument IDs are parsed by `parse_arg_id`, with `parse_context` enforcing that automatic and manual indexing are not mixed. `parse_format_specs` implements alignment, fill, sign, alternate form, zero padding, width, precision, locale, and presentation type validation against the mapped argument type.

Compile-time checking uses `fstring`, `format_string_checker`, `compile_parse_context`, and per-argument formatter `parse` functions when consteval support is available. Runtime strings can opt out through `fmt::runtime`.

## State and Persistence Behavior

Most state is per-call and stack/local: parse contexts hold the remaining format-string view and next argument index; `basic_format_args` is a view over a store; `context` holds output iterator, argument view, and locale reference. Buffers own or reference output storage and flush through destructors or `out()` calls. `basic_format_args` does not own arguments, so storing it beyond the originating call can leave dangling references.

`basic_specs` packs format options into an integer plus a small fill buffer. `value<Context>` is a tagged union for built-in values, strings, pointers, custom format handles, and named argument tables. Custom values keep a raw pointer plus a function pointer to instantiate the relevant formatter.

## Dependencies and Integration Points

The header uses minimal C/C++ headers when not in module mode: limits, stdio, string functions, and type traits. It integrates with fmt `format.h` for definitions of declared formatting functions, native formatter `format` bodies, memory buffers, numeric writers, and platform-specific printing. It also integrates with user `formatter<T>` specializations, `format_as`, named arguments, locale-aware formatting, and Windows mojibake handling.

## Risks and Edge Cases

This is central infrastructure, so ABI and lifetime mistakes have wide blast radius. `basic_format_args` is a non-owning view. Mixing character types is statically rejected. Arbitrary non-void pointers are intentionally disallowed. Dynamic width and precision must resolve to integral arguments. Fill parsing handles multi-code-unit code points and rejects `{` as fill. Compile-time checking depends on compiler consteval support and has fallbacks for older compilers. Output iterator buffering must flush correctly on destruction while avoiding exceptions during unwinding.

## Test Signals

Strong signals include fmt's compile-time and runtime format-string tests, invalid specifier diagnostics, automatic/manual indexing errors, dynamic width and precision validation, named argument lookup, custom formatter dispatch, non-void pointer rejection, Unicode and non-UTF-8 Windows print paths, truncation reporting for fixed arrays, output iterator correctness, locale formatting, and cross-compiler builds with exceptions disabled and old language modes.
