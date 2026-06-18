# sources/user-network-fs/mergerfs/vendored/fmt/printf.h

## Purpose
`printf.h` implements fmt's legacy `printf`-style formatting API. It parses `%` conversion syntax, maps printf flags, width, precision, length modifiers, and conversion specifiers onto fmt's `format_specs`, and exposes `sprintf`, `fprintf`, and `printf` wrappers.

## Important APIs, Types, and Functions
Public types include `basic_printf_context`, `printf_context`, `wprintf_context`, `printf_args`, `wprintf_args`, and `vprintf_args`. Public functions include `make_printf_args`, `vsprintf`, `sprintf`, `vfprintf`, `fprintf`, and `printf`. Internal helpers include `parse_flags`, `parse_header`, `parse_printf_presentation_type`, `vprintf`, `printf_width_handler`, `printf_precision_handler`, `arg_converter`, `char_converter`, `get_cstring`, `is_zero_int`, and `printf_arg_formatter`.

## Control Flow
`sprintf`, `fprintf`, and `printf` create `basic_printf_context` argument stores and call `detail::vprintf`. The parser scans literal text until `%`, treats `%%` as an escaped percent, parses optional positional indexes, flags, width, precision, length modifiers, and conversion type, then fetches the referenced argument. Dynamic `*` width and precision consume arguments. Length modifiers convert integral arguments to the target signed or unsigned width before formatting. The final conversion type is translated to a fmt presentation type, uppercase variants set the upper flag, and `printf_arg_formatter` delegates actual output to the core `detail::write` functions.

## State and Persistence Behavior
All parser state is local to `vprintf`: current iterator, parse context, format specs, and output buffer. The context stores references to caller arguments, so argument lifetimes must outlive formatting. `vsprintf` returns an in-memory string. `vfprintf` writes the completed buffer to the supplied `FILE*` with `std::fwrite`; partial writes return `-1`. `printf` writes to `stdout`. There is no persistent state beyond the effects of writing to the provided C stream.

## Dependencies and Integration Points
The header depends on `format.h` for argument storage, buffers, format specs, type categories, and core write routines, plus `<algorithm>` and `<limits>`. It integrates C-style formatting callers with fmt's type-erased argument system and output buffering. It supports `char` and `wchar_t` contexts, though wide overloads are marked deprecated.

## Risks
This is compatibility formatting, not a byte-for-byte libc `printf` clone. Unsupported or mismatched specifiers report fmt errors, `%n` is not implemented, and some undefined libc cases are intentionally not reproduced. Null strings render as `"(null)"` while null pointers render as `"(nil)"`. Positional and sequential argument modes rely on parse-context checks. Precision handling for C strings scans up to the requested precision and assumes a valid pointer. Argument references must remain valid until formatting completes.

## Test Signals
Useful tests include flags (`-`, `+`, space, `#`, `0`), dynamic width and precision, positional arguments, length modifiers (`hh`, `h`, `l`, `ll`, `j`, `z`, `t`, `L`), integer bases, char/string/pointer conversions, null string and pointer rendering, wide-string deprecated paths, invalid format errors, escaped percent handling, and `fprintf` short-write failure behavior.
