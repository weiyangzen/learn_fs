# File Research: sources/os/bsd/netbsd-src/lib/libc/citrus/citrus_prop.h

Read completely: 91 lines.

This header defines the property parser public interface. It declares `_citrus_prop_type_t`, callback typedefs for booleans, strings, character ranges, and numeric ranges, the `_citrus_prop_hint_t` table format, helper macros for hint entries, and `_citrus_prop_parse_variable`.

Important interactions: modules build static hint arrays with `_CITRUS_PROP_HINT_*` macros, then pass module-local context to the parser. Numeric and character properties use callbacks that receive a start and end value, allowing compact range syntax.

Security/reliability notes: no runtime code here, but the callback signatures define ownership and trust boundaries: string callback arguments are temporary parser-owned strings and must not be retained without copying unless the implementation guarantees lifetime.
