# File Research: sources/virtualization/nbdkit/server/parsing.c

Purpose: Implements exported parsing helpers used by plugins, filters, and server code.

Integer parsing:
- Provides signed parsers for `int`, `int8_t`, `int16_t`, `int32_t`, and `int64_t`.
- Provides unsigned parsers for `unsigned`, `uint8_t`, `uint16_t`, `uint32_t`, and `uint64_t`.
- Signed parsers use `strtol`/`strtoll` with range checks.
- Unsigned parsers reject leading negative signs before calling `strtoul`/`strtoull`.
- Common tail logic rejects empty input, trailing garbage, and range/parse errors, then optionally stores the result.

Other parsers:
- `nbdkit_parse_size` delegates to `human_size_parse`.
- `nbdkit_parse_probability` accepts `N:M`, `N/M`, decimal probabilities, or percentages; rejects NaN, infinity, and negative values.
- `nbdkit_parse_bool` delegates to `parse_bool` and reports user-friendly errors.
- `nbdkit_parse_delay` accepts seconds, milliseconds, microseconds (`us` or `μs`), and nanoseconds, returning seconds plus nanoseconds.

Compatibility:
- Suppresses GCC 12+ `-Wnonnull-compare` noise because older plugins may still pass null despite newer nonnull declarations.
